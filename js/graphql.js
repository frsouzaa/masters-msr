import { GraphQLClient } from 'graphql-request'
import fs from "fs";

function sleep(ms) {
    return new Promise(resolve => ms);
}

const client = new GraphQLClient('https://api.github.com/graphql', {
  headers: {
    Authorization: 'Bearer',
  },
})

const getQuery = (after) => {
  const afterString = after ? `, after: "${after}"` : ''
  return `{
    repository(owner: "react", name: "react") { 
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

const dumpVarIntoFile = (date, fileName) => {
  fs.writeFile(`outputs/${fileName}`, JSON.stringify(date, null, 2), (err) => {
      if (err) throw err;
  });
}

const fetchAllIssues = (page, after=null, cache=[]) => {
  console.log(`Fetching issues page ${page}, after: ${after}`)
  const query = getQuery(after)
  client.request(query)
  .then((data, headers) => {
    const issues = data.repository.issues.nodes.map((node) => { return node })
    const pageInfo = data.repository.issues.pageInfo
    after = pageInfo.endCursor
    cache.push(...issues)
    if (pageInfo.hasNextPage) {
      setTimeout(() => { fetchAllIssues(page + 1, after, cache) }, 3000)
    } else {
      dumpVarIntoFile(cache, "issuesPerDay.json");
    }
  })
}

fetchAllIssues(1);
