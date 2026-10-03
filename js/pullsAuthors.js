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

const queuePullDetails = (pulls) => {
  for (let i=0; i < pulls.length; i++) {
    if (pulls[i].merged_at !== null && pulls[i].merged_by === null) {
      const request = new GitHubApiRequest(
        `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/pulls/${pulls[i].number}`,
        {},
        (result) => {
          console.log(`Pulls - PR ${pulls[i].number} encontrado com sucesso`);
          pulls[i].merged_by = result.data.merged_by ? result.data.merged_by.login : null
          if (queue.getQueueLength() === 0) {
            dumpVarIntoFile(pulls, "per_day_pulls");
            queue.stop();
          }
        }
      );
      queue.push(request);
    }
    if (pulls[i].closed_at !== null && pulls[i].closed_by === null) {
      const request = new GitHubApiRequest(
        `${GH_API_BASE_URL}/repos/${REPO_OWNER_NAME}/issues/${pulls[i].number}`,
        {},
        (result) => {
          console.log(`Pulls - PR ${pulls[i].number} encontrado com sucesso`);
          pulls[i].closed_by = result.data.closed_by ? result.data.closed_by.login : null
          if (queue.getQueueLength() === 0) {
            dumpVarIntoFile(pulls, "per_day_pulls");
            queue.stop();
          }
        }
      );
      queue.push(request);
    }
  }
}

const pulls = await parseCSVFile("outputs/per_day_pulls.csv");

queuePullDetails(pulls);

queue.start();
