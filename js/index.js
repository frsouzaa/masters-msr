import { GitHubApiRequest, GitHubApiClient, GitHubApiQueue } from "poolingh";
import { json2csv } from "json-2-csv";
import fs from "fs";

const GH_API_BASE_URL = "https://api.github.com";
const GH_TOKEN = process.env.GH_TOKEN;
const REPO_OWNER_NAME = process.env.REPO_URL.split("github.com/")[1];
const REPO_OWNER = process.env.REPO_URL.split("github.com/")[1].split("/")[0];
const REPO_NAME = process.env.REPO_URL.split("github.com/")[1].split("/")[1];
const STARS_API_PER_PAGE = 30; // https://docs.github.com/en/rest/activity/starring?apiVersion=2026-03-10#get-repository-star-history
const FORKS_API_PER_PAGE = 100; // https://docs.github.com/en/rest/repos/forks?apiVersion=2026-03-10#list-forks
const PULLS_API_PER_PAGE = 100; // https://docs.github.com/en/rest/pulls/pulls?apiVersion=2026-03-10#list-pull-requests
const ISSUES_API_PER_PAGE = 100; // https://docs.github.com/en/rest/issues/issues?apiVersion=2026-03-10#list-repository-issues

const getApiClient = () => {
  return new GitHubApiClient(GH_TOKEN, 10, 5000);
}

const getWeeksBetween = (date1, date2) => {
  // 1000ms * 60s * 60m * 24h * 7 days = milliseconds in one week
  const MS_IN_WEEK = 1000 * 60 * 60 * 24 * 7;
  // Get the absolute difference in milliseconds
  const diffInMs = Math.abs(date2 - date1);
  // Return full weeks (use Math.round or Math.ceil if you prefer partial weeks)
  return Math.ceil(diffInMs / MS_IN_WEEK);
}

const dumpVarIntoFile = (date, fileName) => {
  fs.writeFile(`outputs/${fileName}.csv`, json2csv(date), (err) => {
    if (err) throw err;
  });
}

const queueStarsPerDay = (queue) => {
  const starsPerDay = [];
  const request = new GitHubApiRequest(
    `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}`,
    {},
    (result) => {
      console.log(`Stars - Repository ${REPO_OWNER_NAME} found, creation date: ${result.data.created_at}`);
      const number_of_pages = Math.ceil(getWeeksBetween(new Date(result.data.created_at), new Date()) / STARS_API_PER_PAGE);
      for (let i = 1; i <= number_of_pages; i++) {
        const request = new GitHubApiRequest(
          `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/stargazers/history?per_page=${STARS_API_PER_PAGE}&page=${i}`,
          {},
          (result) => {
            console.log(`Stars - page ${i}`);
            for (let j = 0; j < result.data.length; j++) {
              for (let k = 0; k < result.data[j].days.length; k++) {
                starsPerDay.push({
                  date: new Date((result.data[j].week + k * 24 * 60 * 60) * 1000).toISOString().split("T")[0], // convertendo para timestamp
                  count: result.data[j].days[k],
                });
              }
            }
            if (i === 1) {
              dumpVarIntoFile(starsPerDay, "per_day_stars");
              if (queue.getQueueLength() === 0) {
                queue.stop();
              }
            }
          }
        );
        queue.push(request);
      }
    }
  )
  queue.push(request);
}

const queueForksPerDay = (queue) => {
  const forksPerDay = [];
  const request = new GitHubApiRequest(
    `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}`,
    {},
    (result) => {
      console.log(`Forks - Repository ${REPO_OWNER_NAME} found, fork count: ${result.data.forks_count}`);
      const number_of_pages = Math.ceil(result.data.forks_count / FORKS_API_PER_PAGE);
      for (let i = 1; i <= number_of_pages; i++) {
        const request = new GitHubApiRequest(
          `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/forks?per_page=${FORKS_API_PER_PAGE}&page=${i}&sort=newest`,
          {},
          (result) => {
            console.log(`Forks - page ${i}`);
            forksPerDay.push(...result.data.map(fork => ({
              html_url: fork.html_url,
              date: fork.created_at.split("T")[0],
              count: 1,
            })));
            if (i === 1) {
              dumpVarIntoFile(forksPerDay, "per_day_forks");
              if (queue.getQueueLength() === 0) {
                queue.stop();
              }
            }
          }
        );
        queue.push(request);
      }
    }
  );
  queue.push(request);
}

const queuePullsPerDay = (queue, page = 1, after = null, cache = []) => {
  const afterString = after ? `, after: "${after}"` : ""
  const request = new GitHubApiRequest(
    `${GH_API_BASE_URL}/graphql`,
    {
      method: "POST",
      body: JSON.stringify({
        query: `{
          repository(owner: "${REPO_OWNER}", name: "${REPO_NAME}") { 
            pullRequests(first: ${PULLS_API_PER_PAGE} ${afterString}) {
              nodes {
                repository {
                  databaseId
                }
                url
                number
                createdAt
                closedAt
                mergedAt
                author {
                  login
                }
                timelineItems(itemTypes: [CLOSED_EVENT], last: 1) {
                  nodes {
                    ... on ClosedEvent {
                      actor {
                        login
                      }
                    }
                  }
                }
                mergedBy {
                  login
                }
              }
              pageInfo {
                endCursor
                startCursor
                hasNextPage
                hasPreviousPage
              }
            }
          }
        }`
      })
    },
    (result) => {
      const nodes = result.data.data.repository.pullRequests.nodes;
      const pageInfo = result.data.data.repository.pullRequests.pageInfo;
      console.log(`Pulls - page ${page}, after ${after}`);
      cache.push(...nodes.map(pull => ({
        repo_id: pull.repository.databaseId,
        number: pull.number,
        html_url: pull.url,
        created_at: pull.createdAt.split("T")[0],
        closed_at: pull.closedAt ? pull.closedAt.split("T")[0] : null,
        merged_at: pull.mergedAt ? pull.mergedAt.split("T")[0] : null,
        created_by: pull.author ? pull.author.login : null,
        closed_by: pull.timelineItems.nodes[0] && pull.timelineItems.nodes[0].actor ? pull.timelineItems.nodes[0].actor.login : null,
        merged_by: pull.mergedBy ? pull.mergedBy.login : null,
        count: 1,
      })));
      if (!pageInfo.hasNextPage) {
        dumpVarIntoFile(cache, "per_day_pulls");
        if (queue.getQueueLength() === 0) {
          queue.stop();
        }
        return;
      }
      queuePullsPerDay(queue, page + 1, pageInfo.endCursor, cache);
    }
  );
  queue.push(request);
}

const queueIssuesPerDay = (queue, page=1, after=null, cache=[]) => {
  const afterString = after ? `, after: "${after}"` : ""
  const request = new GitHubApiRequest(
    `${GH_API_BASE_URL}/graphql`,
    {
      method: "POST",
      body: JSON.stringify({
        query: `{
          repository(owner: "${REPO_OWNER}", name: "${REPO_NAME}") { 
            issues(first: ${ISSUES_API_PER_PAGE} ${afterString}) {
              nodes {
                repository {
                  databaseId
                }
                url
                number
                createdAt
                closedAt
                author {
                  login
                }
                timelineItems(itemTypes: [CLOSED_EVENT], last: 1) {
                  nodes {
                    ... on ClosedEvent {
                      actor {
                        login
                      }
                    }
                  }
                }
              }
              pageInfo {
                endCursor
                startCursor
                hasNextPage
                hasPreviousPage
              }
            }
          }
        }`
      })
    },
    (result) => {
      const nodes = result.data.data.repository.issues.nodes;
      const pageInfo = result.data.data.repository.issues.pageInfo;
      console.log(`Issues - page ${page}, after ${after}`);
      cache.push(...nodes.map(issue => ({
        repo_id: issue.repository.databaseId,
        number: issue.number,
        html_url: issue.url,
        created_at: issue.createdAt.split("T")[0],
        closed_at: issue.closedAt ? issue.closedAt.split("T")[0] : null,
        created_by: issue.author ? issue.author.login : null,
        closed_by: issue.timelineItems.nodes[0] && issue.timelineItems.nodes[0].actor ? issue.timelineItems.nodes[0].actor.login : null,
        count: 1,
      })));
      if (!pageInfo.hasNextPage) {
        dumpVarIntoFile(cache, "per_day_issues");
        if (queue.getQueueLength() === 0) {
          queue.stop();
        }
        return;
      }
      queueIssuesPerDay(queue, page + 1, pageInfo.endCursor, cache);
    }
  );
  queue.push(request);
}

let queue = new GitHubApiQueue([getApiClient()]);

queueStarsPerDay(queue);
queueForksPerDay(queue);
queuePullsPerDay(queue);
queueIssuesPerDay(queue);

queue.start();
