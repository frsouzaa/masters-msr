import { GitHubApiRequest, GitHubApiClient, GitHubApiQueue } from "poolingh";

const GH_TOKEN = process.env.GH_TOKEN;
const REPO_NAME = "star-history/star-history";
const STARS_API_PER_PAGE = 30; // https://docs.github.com/en/rest/activity/starring?apiVersion=2026-03-10#get-repository-star-history

let client1 = new GitHubApiClient(GH_TOKEN, 10, 5000);

let queue = new GitHubApiQueue([client1]);

const stars_per_day = [];

function getWeeksBetween(date1, date2) {
    // 1000ms * 60s * 60m * 24h * 7 days = milliseconds in one week
    const MS_IN_WEEK = 1000 * 60 * 60 * 24 * 7;
    // Get the absolute difference in milliseconds
    const diffInMs = Math.abs(date2 - date1);
    // Return full weeks (use Math.round or Math.ceil if you prefer partial weeks)
    return Math.ceil(diffInMs / MS_IN_WEEK);
}

let request = new GitHubApiRequest(
  `https://api.github.com/repos/${REPO_NAME}`,
  {},
  (result) => {
    console.log(`Repositório ${REPO_NAME} encontrado com sucesso, data de criação: ${result.data.created_at}`);
    const number_of_pages = Math.ceil(getWeeksBetween(new Date(result.data.created_at), new Date()) / STARS_API_PER_PAGE);
    for (let i = 1; i <= number_of_pages; i++) {
      let request = new GitHubApiRequest(
        `https://api.github.com/repos/${REPO_NAME}/stargazers/history?per_page=${STARS_API_PER_PAGE}&page=${i}`,
        {},
        (result) => {
          console.log(`Página ${i} processada com sucesso!`);
          for (let j = 0; j < result.data.length; j++) {
            for (let k = 0; k < result.data[j].days.length; k++) {
              stars_per_day.push({
                date: new Date((result.data[j].week + k * 24 * 60 * 60) * 1000), // convertendo para timestamp
                count: result.data[j].days[k],
              });
            }
          }
          if (i === 1) {
            console.log("Todas as páginas foram processadas com sucesso!");
            queue.stop();
          }
        }
      );
      queue.push(request);
    }
  }
)

queue.push(request);

// últimos 4 anos ~= 210 semanas
// paginação de 30 em 30, então 210 / 30 = 7 páginas

queue.start();
