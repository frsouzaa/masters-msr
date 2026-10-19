import json

with open('results.json') as json_data:
    d = json.load(json_data)

all_languages = {}
for repo in d["items"]:
    all_languages[repo["mainLanguage"]] = all_languages.get(repo["mainLanguage"], 0) + 1
    
most_used_language = list(dict(sorted(all_languages.items(), key=lambda item: item[1], reverse=True)).items())[0:10]

languages_repos = {lang: [] for lang, _ in most_used_language}

for repo in d["items"]:
    if repo["mainLanguage"] in languages_repos:
        languages_repos[repo["mainLanguage"]].append(repo)

for language, repos in languages_repos.items():
    print(f"{language} repos found: {len(repos)} -> {len(repos)/len(d["items"])*100}%")

for language, repos in languages_repos.items():
    most_starred_repos = sorted(repos, key=lambda item: item["stargazers"], reverse=True)[0:15]
    print(f"{language} most starred repos:")
    for repo in most_starred_repos:
        print(f"  https://github.com/{repo['name']}: {repo['stargazers']} stars")
