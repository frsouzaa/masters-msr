import { GitHubApiRequest, GitHubApiClient, GitHubApiQueue } from "poolingh";
import { json2csv } from "json-2-csv";
import { parse } from "csv-parse";
import fs from "fs";

const GH_API_BASE_URL = "https://api.github.com";
const GH_TOKEN = process.env.GH_TOKEN;
const REPO_OWNER_NAME = process.env.REPO_URL.split("github.com/")[1];

const getApiClient = () => {
  return new GitHubApiClient(GH_TOKEN, 10, 5000);
}

const dumpVarIntoFile = (date, fileName) => {
  fs.writeFile(`outputs/${fileName}.csv`, json2csv(date), (err) => {
    if (err) throw err;
  });
}

let queue = new GitHubApiQueue([getApiClient()]);

const parseCSVFile = async (filePath) => {
  return new Promise((resolve, reject) => {
    const path = filePath;
    const stream = fs.createReadStream(path);
    const parser = parse();
    const content = [];
    stream.on("ready", () => {
      stream.pipe(parser);
    });
    parser.on("readable", function () {
      const headers = parser.read();
      let record;
      while (record = parser.read()) {
        const toJson = {};
        for (let i = 0; i < headers.length; i++) {
          if (record[i] === "null") {
            toJson[headers[i]] = null;
          } else {
            toJson[headers[i]] = record[i];
          }
        }
        content.push(toJson)
      }
    });
    parser.on("error", function (err) {
      console.error(err.message)
      reject();
    });
    parser.on("end", function () {
      resolve(content);
    });
  });
}

const queuePullDetails = (issues) => {
  for (let i=0; i < issues.length; i++) {
    if (issues[i].closed_at !== null && issues[i].closed_by === null) {
      const request = new GitHubApiRequest(
        `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/issues/${issues[i].number}`,
        {},
        (result) => {
          console.log(`Issues - Issue ${issues[i].number} encontrado com sucesso`);
          issues[i].closed_by = result.data.closed_by ? result.data.closed_by.login : null
          if (queue.getQueueLength() === 0) {
            dumpVarIntoFile(issues, "issuesPerDayAuthors");
            queue.stop();
          }
        }
      );
      queue.push(request);
    }
  }
}

const issues = await parseCSVFile("outputs/issuesPerDay.csv");

queuePullDetails(issues);

queue.start();
