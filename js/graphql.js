import { GraphQLClient } from 'graphql-request'
import { json2csv } from 'json-2-csv';
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

const getQuery = (after) => {
  const afterString = after ? `, after: "${after}"` : ''
  return `{
    repository(owner: "${REPO_OWNER}", name: "${REPO_NAME}") { 
      issues(first: 100 ${afterString}) {
        nodes {
          url
          createdAt
          closedAt
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

const client = new GraphQLClient('https://api.github.com/graphql', {
  headers: {
    Authorization: `Bearer ${GH_TOKEN}`,
  },
})

const fetchAllIssues = (page, after=null, cache=[]) => {
  console.log(`Fetching issues page ${page}, after: ${after}`)
  const query = getQuery(after)
  client.request(query)
  .then((data, headers) => {
    const issues = data.repository.issues.nodes.map((node) => { return node })
    const pageInfo = data.repository.issues.pageInfo
    after = pageInfo.endCursor
    cache.push(...issues.map(issue => ({
      html_url: issue.url,
      created_at: issue.createdAt.split('T')[0],
      closed_at: issue.closedAt ? issue.closedAt.split('T')[0] : null,
      count: 1,
    })));
    if (pageInfo.hasNextPage) {
      setTimeout(() => { fetchAllIssues(page + 1, after, cache) }, 3000)
    } else {
      dumpVarIntoFile(cache, "issuesPerDay");
    }
  })
}

fetchAllIssues(1);
