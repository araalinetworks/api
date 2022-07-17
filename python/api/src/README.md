# A note on Git and LFS
In general it is a bad idea to commit binary files into git. But when you do
there is git lfs to the rescue

## Install LFS
```
brew install git-lfs
```

## Add LFS capabilities to your repo (one time)
```
git lfs install
```

## Before git adding files, mark them as large files
```
git lfs track <path>

# for e.g. to add more files to be tracked under lfs,
# replace the binary file eg below
# (araalictl.darwin-amd64)
git lfs track araali/bin/araalictl.darwin-amd64
