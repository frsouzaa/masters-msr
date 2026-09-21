import { GitHubApiRequest, GitHubApiClient, GitHubApiQueue } from "poolingh";
import { json2csv } from 'json-2-csv';
import fs from "fs";

const GH_API_BASE_URL = "https://api.github.com";
const GH_TOKEN = process.env.GH_TOKEN;
const REPO_OWNER_NAME = process.env.REPO_URL.split("github.com/")[1];
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
  fs.writeFile(`outputs/${fileName}.json`, JSON.stringify(date, null, 2), (err) => {
      if (err) throw err;
  });
}

const queueStarsPerDay = (queue) => {
  const starsPerDay = [];
  const request = new GitHubApiRequest(
    `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}`,
    {},
    (result) => {
      console.log(`Stars - Repositório ${REPO_OWNER_NAME} encontrado com sucesso, data de criação: ${result.data.created_at}`);
      const number_of_pages = Math.ceil(getWeeksBetween(new Date(result.data.created_at), new Date()) / STARS_API_PER_PAGE);
      for (let i = 1; i <= number_of_pages; i++) {
        const request = new GitHubApiRequest(
          `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/stargazers/history?per_page=${STARS_API_PER_PAGE}&page=${i}`,
          {},
          (result) => {
            console.log(`Stars - Página ${i} processada com sucesso!`);
            for (let j = 0; j < result.data.length; j++) {
              for (let k = 0; k < result.data[j].days.length; k++) {
                starsPerDay.push({
                  date: new Date((result.data[j].week + k * 24 * 60 * 60) * 1000).toISOString().split('T')[0], // convertendo para timestamp
                  count: result.data[j].days[k],
                });
              }
            }
            if (i === 1) {
              console.log("Stars - Todas as páginas foram processadas com sucesso!");
              dumpVarIntoFile(starsPerDay, "starsPerDay");
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
      console.log(`Forks - Repositório ${REPO_OWNER_NAME} encontrado com sucesso, quantidade de forks: ${result.data.forks_count}`);
      const number_of_pages = Math.ceil(result.data.forks_count / FORKS_API_PER_PAGE);
      for (let i = 1; i <= number_of_pages; i++) {
        const request = new GitHubApiRequest(
          `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/forks?per_page=${FORKS_API_PER_PAGE}&page=${i}&sort=newest`,
          {},
          (result) => {
            console.log(`Forks - Página ${i} processada com sucesso, quantidade de forks encontrados na página: ${result.data.length}`);
            forksPerDay.push(...result.data.map(fork => ({
              html_url: fork.html_url,
              date: fork.created_at.split('T')[0],
              count: 1,
            })));
            if (i === 1) {
              console.log("Forks - Todas as páginas foram processadas com sucesso!");
              dumpVarIntoFile(forksPerDay, "forksPerDay");
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

const queuePullsPerDay = (queue, page=1, cache=[]) => {
  const request = new GitHubApiRequest(
    `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/pulls?per_page=${PULLS_API_PER_PAGE}&page=${page}&state=all`,
    {},
    (result) => {
      console.log(`Pulls - Página ${page} processada com sucesso, quantidade de pull requests encontrados na página: ${result.data.length}`);
      cache.push(...result.data.map(pull => ({
        html_url: pull.html_url,
        created_at: pull.created_at.split('T')[0],
        closed_at: pull.closed_at ? pull.closed_at.split('T')[0] : null,
        merged_at: pull.merged_at ? pull.merged_at.split('T')[0] : null,
        count: 1,
      })));
      if (result.data.length < PULLS_API_PER_PAGE) {
        dumpVarIntoFile(cache, "pullsPerDay");
        if (queue.getQueueLength() === 0) {
          queue.stop();
        }
        return;
      }
      queuePullsPerDay(queue, page + 1, cache);
    }
  );
  queue.push(request);
}

// Rest API não funciona para projetos com mais de 10000 issues, a alternativa é utilizar GraphQL
// const queueIssuesPerDay = (queue, page=1, cache=[]) => {
//   const request = new GitHubApiRequest(
//     `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/issues?per_page=${ISSUES_API_PER_PAGE}&page=${page}&state=all`,
//     {},
//     (result) => {
//       console.log(`Issues - Página ${page} processada com sucesso, quantidade de issues encontrados na página: ${result.data.length}`);
//       cache.push(...result.data.filter(issue => issue.pull_request == null).map(issue => ({
//         html_url: issue.html_url,
//         created_at: issue.created_at.split('T')[0],
//         closed_at: issue.closed_at ? issue.closed_at.split('T')[0] : null,
//         merged_at: issue.merged_at ? issue.merged_at.split('T')[0] : null,
//         count: 1,
//       })));
//       if (result.data.length < ISSUES_API_PER_PAGE) {
//         dumpVarIntoFile(cache, "issuesPerDay");
//         if (queue.getQueueLength() === 0) {
//           queue.stop();
//         }
//         return;
//       }
//       queueIssuesPerDay(queue, page + 1, cache);
//     }
//   );
//   queue.push(request);
// }

let queue = new GitHubApiQueue([getApiClient()]);

queueStarsPerDay(queue);
queueForksPerDay(queue);
queuePullsPerDay(queue);
queue.start();
