# Allowed Tools

This is a comprehensive list of tools that agents can utilize during task execution. Not all tools are useful to each agent - choose carefully based on the role and the specific requirements of the task

## Task

Launch a new agent to handle complex, multi-step tasks autonomously

## Bash

Executes a given bash command in a persistent shell session with optional timeout, ensuring proper handling and security measures

## Glob

Fast file pattern matching tool that works with any codebase size

## Grep

A powerful search tool built on ripgrep

## LS

Lists files and directories in a given path

## Read

Reads a file from the local filesystem

## Edit

Performs exact string replacements in files

## MultiEdit

This is a tool for making multiple edits to a single file in one operation

## Write

Writes a file to the local filesystem

## NotebookRead

Reads a Jupyter notebook (.ipynb file) and returns all of the cells with their outputs

## NotebookEdit

Completely replaces the contents of a specific cell in a Jupyter notebook (.ipynb file) with new source

## WebFetch

Fetches content from a specified URL and processes it using an AI model

## TodoWrite

Use this tool to create and manage a structured task list for your current coding session

## WebSearch

Search the web and use the results to inform responses

## ListMcpResourcesTool

List available resources from configured MCP servers

## ReadMcpResourceTool

Reads a specific resource from an MCP server

## mcp__github__add_issue_comment

Add a comment to a specific issue in a GitHub repository

## mcp__github__add_pull_request_review_comment_to_pending_review

Add a comment to the requester's latest pending pull request review, a pending review needs to already exist to call this (check with the user if not sure)

## mcp__github__assign_copilot_to_issue

Assign Copilot to a specific issue in a GitHub repository

## mcp__github__create_and_submit_pull_request_review

Create and submit a review for a pull request without review comments

## mcp__github__create_branch

Create a new branch in a GitHub repository

## mcp__github__create_issue

Create a new issue in a GitHub repository

## mcp__github__create_or_update_file

Create or update a single file in a GitHub repository

## mcp__github__create_pending_pull_request_review

Create a pending review for a pull request

## mcp__github__create_pull_request

Create a new pull request in a GitHub repository

## mcp__github__create_repository

Create a new GitHub repository in your account

## mcp__github__delete_file

Delete a file from a GitHub repository

## mcp__github__delete_pending_pull_request_review

Delete the requester's latest pending pull request review

## mcp__github__fork_repository

Fork a GitHub repository to your account or specified organization

## mcp__github__get_code_scanning_alert

Get details of a specific code scanning alert in a GitHub repository

## mcp__github__get_commit

Get details for a commit from a GitHub repository

## mcp__github__get_file_contents

Get the contents of a file or directory from a GitHub repository

## mcp__github__get_issue

Get details of a specific issue in a GitHub repository

## mcp__github__get_issue_comments

Get comments for a specific issue in a GitHub repository

## mcp__github__get_me

Get details of the authenticated GitHub user

## mcp__github__get_pull_request

Get details of a specific pull request in a GitHub repository

## mcp__github__get_pull_request_comments

Get comments for a specific pull request

## mcp__github__get_pull_request_diff

Get the diff of a pull request

## mcp__github__get_pull_request_files

Get the files changed in a specific pull request

## mcp__github__get_pull_request_reviews

Get reviews for a specific pull request

## mcp__github__get_pull_request_status

Get the status of a specific pull request

## mcp__github__get_secret_scanning_alert

Get details of a specific secret scanning alert in a GitHub repository

## mcp__github__get_tag

Get details about a specific git tag in a GitHub repository

## mcp__github__list_branches

List branches in a GitHub repository

## mcp__github__list_code_scanning_alerts

List code scanning alerts in a GitHub repository

## mcp__github__list_commits

Get list of commits of a branch in a GitHub repository

## mcp__github__list_issues

List issues in a GitHub repository

## mcp__github__list_pull_requests

List pull requests in a GitHub repository

## mcp__github__list_tags

List git tags in a GitHub repository

## mcp__github__merge_pull_request

Merge a pull request in a GitHub repository

## mcp__github__push_files

Push multiple files to a GitHub repository in a single commit

## mcp__github__request_copilot_review

Request a GitHub Copilot code review for a pull request. Use this for automated feedback on pull requests, usually before requesting a human reviewer

## mcp__github__search_code

Search for code across GitHub repositories

## mcp__github__search_issues

Search for issues in GitHub repositories

## mcp__github__search_repositories

Search for GitHub repositories

## mcp__github__search_users

Search for GitHub users

## mcp__github__submit_pending_pull_request_review

Submit the requester's latest pending pull request review

## mcp__github__update_issue

Update an existing issue in a GitHub repository

## mcp__github__update_pull_request

Update an existing pull request in a GitHub repository

## mcp__github__update_pull_request_branch

Update the branch of a pull request with the latest changes from the base branch

## mcp__context7__resolve-library-id

Resolves a package/product name to a Context7-compatible library ID and returns a list of matching libraries

## mcp__context7__get-library-docs

Fetches up-to-date documentation for a library

## mcp__notion__search

Perform a search over notion and connected sources

## mcp__notion__fetch

Retrieves details about a Notion entity

## mcp__notion__create-pages

Creates one or more Notion pages with specified properties and content

## mcp__notion__update-page

Update a Notion page's properties or content

## mcp__notion__move-pages

Move one or more Notion pages or databases to a new parent

## mcp__notion__duplicate-page

Duplicate a Notion page

## mcp__notion__create-database

Creates a new Notion database with the specified properties

## mcp__notion__update-database

Update a Notion database's properties, name, description, or other attributes

## mcp__notion__create-comment

Add a comment to a page

## mcp__notion__get-comments

Get all comments of a page

## mcp__notion__get-users

List all users

## mcp__notion__get-self

Retrieve your token's bot user

## mcp__notion__get-user

Retrieve a user

## mcp__ide__getDiagnostics

Get language diagnostics from VS Code

## mcp__ide__executeCode

Execute python code in the Jupyter kernel for the current notebook file

## mcp__browseruse__browser_navigate

Navigate to a URL in the browser

## mcp__browseruse__browser_click

Click an element on the page by its index

## mcp__browseruse__browser_type

Type text into an input field

## mcp__browseruse__browser_get_state

Get the current state of the page including all interactive elements

## mcp__browseruse__browser_extract_content

Extract structured content from the current page based on a query

## mcp__browseruse__browser_scroll

Scroll the page

## mcp__browseruse__browser_go_back

Go back to the previous page

## mcp__browseruse__browser_list_tabs

List all open tabs

## mcp__browseruse__browser_switch_tab

Switch to a different tab

## mcp__browseruse__browser_close_tab

Close a tab

## mcp__browseruse__retry_with_browser_use_agent

Retry a task using the browser-use agent
