import { GraphQLClient } from "graphql-request"
import { json2csv } from "json-2-csv";
import fs from "fs";

const GH_TOKEN = process.env.GH_TOKEN;
const REPO_OWNER = process.env.REPO_URL.split("github.com/")[1].split("/")[0];
const REPO_NAME = process.env.REPO_URL.split("github.com/")[1].split("/")[1];


const sleep = (ms) => {
  return new Promise(resolve => ms);
}

const dumpVarIntoFile = (date, fileName) => {
  fs.writeFile(`outputs/${fileName}.csv`, json2csv(date), (err) => {
    if (err) throw err;
  });
}

const getIssuesQuery = (after) => {
  const afterString = after ? `, after: "${after}"` : ""
  return `{
    repository(owner: "${REPO_OWNER}", name: "${REPO_NAME}") { 
      issues(first: 100 ${afterString}) {
        nodes {
          url
          number
          createdAt
          closedAt
          author {
            ... on User {
              login
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
}

const getPullsQuery = (after) => {
  const afterString = after ? `, after: "${after}"` : ""
  return `{
    repository(owner: "${REPO_OWNER}", name: "${REPO_NAME}") { 
      pullRequests(first: 100 ${afterString}) {
        nodes {
          url
          number
          createdAt
          closedAt
          mergedAt
          author {
            ... on User {
              login
            }
          }
          mergedBy {
            ... on User {
              login
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
}

const client = new GraphQLClient("https://api.github.com/graphql", {
  headers: {
    Authorization: `Bearer ${GH_TOKEN}`,
  },
})

const fetchAllIssues = (page, after = null, cache = []) => {
  console.log(`Fetching issues page ${page}, after: ${after}`)
  const query = getIssuesQuery(after)
  client.request(query)
    .then((data, headers) => {
      const issues = data.repository.issues.nodes.map((node) => { return node })
      const pageInfo = data.repository.issues.pageInfo
      after = pageInfo.endCursor
      cache.push(...issues.map(issue => ({
        number: issue.number,
        html_url: issue.url,
        created_at: issue.createdAt.split("T")[0],
        closed_at: issue.closedAt ? issue.closedAt.split("T")[0] : null,
        created_by: issue.author ? issue.author.login : null,
        closed_by: null,
        count: 1,
      })));
      if (pageInfo.hasNextPage) {
        setTimeout(() => { fetchAllIssues(page + 1, after, cache) }, 3000)
      } else {
        dumpVarIntoFile(cache, "issuesPerDay");
      }
    })
}

const fetchAllPulls = (page, after = null, cache = []) => {
  console.log(`Fetching pulls page ${page}, after: ${after}`)
  const query = getPullsQuery(after)
  client.request(query)
    .then((data, headers) => {
      const pulls = data.repository.pullRequests.nodes.map((node) => { return node })
      const pageInfo = data.repository.pullRequests.pageInfo
      after = pageInfo.endCursor
      cache.push(...pulls.map(pull => ({
        number: pull.number,
        html_url: pull.url,
        created_at: pull.createdAt.split("T")[0],
        closed_at: pull.closedAt ? pull.closedAt.split("T")[0] : null,
        merged_at: pull.mergedAt ? pull.mergedAt.split("T")[0] : null,
        created_by: pull.author ? pull.author.login : null,
        closed_by: null,
        merged_by: pull.mergedBy ? pull.mergedBy.login : null,
        count: 1,
      })));
      if (pageInfo.hasNextPage) {
        setTimeout(() => { fetchAllPulls(page + 1, after, cache) }, 3000)
      } else {
        dumpVarIntoFile(cache, "pullsPerDay");
      }
    })
}

// fetchAllIssues(1);
fetchAllPulls(1);
