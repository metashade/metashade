# Contributing to Metashade

Thank you for your interest in contributing to Metashade! We welcome contributions of all kinds — bug fixes, new features, documentation improvements, and more.

## Developer Certificate of Origin (DCO)

All contributions to this repository must include a `Signed-off-by` line in each commit message. By signing off, you certify that you have the right to submit the code under the project's open-source license, in accordance with the [Developer Certificate of Origin (DCO)](https://developercertificate.org/).

To sign your commit, use the `-s` flag:

```bash
git commit -s -m "Your commit message"
```

This will add a line like the following to your commit message:

```
Signed-off-by: Your Name <your.email@example.com>
```

### Fixing Unsigned Commits

If you forgot to sign a commit, you can amend the most recent one:

```bash
git commit --amend --no-edit --signoff
git push --force-with-lease
```
