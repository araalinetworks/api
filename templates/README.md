# Getting Started
```
# pull templates from araali
# sync/merge with master (template as code)
# check if there is any drift
make pull

# push templates to araali
make push

# push templates to git
git commit
git push
```
# Links
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
* https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/testing-your-ssh-connection
* https://docs.github.com/en/github/using-git/changing-a-remotes-url

# Troubleshooting
## Authorization problems
```
./araalictl authorize -clean # to start over.
```
## Not able to push your branch
- https://docs.github.com/en/github/using-git/changing-a-remotes-url
- https://docs.github.com/en/free-pro-team@latest/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
