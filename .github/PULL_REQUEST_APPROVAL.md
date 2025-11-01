# Pull Request Approval Configuration

This repository is configured to ensure that only the repository owner can approve pull requests.

## Configuration

### CODEOWNERS File

The `.github/CODEOWNERS` file designates `@D1odeKing` as the code owner for all files in this repository. This means:

- All pull requests will automatically request a review from @D1odeKing
- GitHub will show that a review from the code owner is required

### Branch Protection Rules (Required Setup)

To **enforce** that only the repository owner can approve pull requests, you must configure branch protection rules in GitHub:

#### Setup Steps:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Branches**
3. Click **Add branch protection rule** (or edit existing rule)
4. For "Branch name pattern", enter: `main` (or your default branch name)
5. Enable the following settings:
   - ✅ **Require a pull request before merging**
   - ✅ **Require approvals** (set to at least 1)
   - ✅ **Require review from Code Owners** ⭐ (This is the key setting)
   - ✅ **Dismiss stale pull request approvals when new commits are pushed** (recommended)
   - ✅ **Restrict who can dismiss pull request reviews** (optional but recommended)
6. Optionally enable:
   - ✅ **Do not allow bypassing the above settings** (prevents admin override)
   - ✅ **Require status checks to pass before merging** (if you have CI/CD)
7. Click **Create** or **Save changes**

#### What This Does:

- **Require review from Code Owners**: Since @D1odeKing is designated as the code owner for all files, this setting ensures that @D1odeKing's approval is required before any pull request can be merged.
- **Only the designated code owner** (you) will be able to provide the approval that satisfies the merge requirement.
- Other contributors can still review and comment on pull requests, but their approvals won't satisfy the code owner requirement.

### Additional Security (Optional):

For maximum control, you can also:

1. **Limit who can push to protected branches**:
   - In the same branch protection settings, scroll to "Restrict who can push to matching branches"
   - Add only your username to allow direct pushes (if needed)

2. **Require signed commits**:
   - Enable "Require signed commits" in branch protection rules
   - This adds an extra layer of verification

## Verification

To verify the setup is working:

1. Create a test pull request from a different account or branch
2. You should see that a review from @D1odeKing is required
3. The pull request cannot be merged until @D1odeKing approves it

## Notes

- The CODEOWNERS file is automatically recognized by GitHub when placed in `.github/`, `docs/`, or the root directory
- Branch protection rules are **repository settings** that cannot be configured via code files alone
- You must have admin access to the repository to configure branch protection rules
- These settings apply to all contributors, including repository collaborators

## Support

For more information about code owners and branch protection, see:
- [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Managing a branch protection rule](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)
