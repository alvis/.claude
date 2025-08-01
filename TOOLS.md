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

## mcp**github**add_issue_comment

Add a comment to a specific issue in a GitHub repository

## mcp**github**add_pull_request_review_comment_to_pending_review

Add a comment to the requester's latest pending pull request review, a pending review needs to already exist to call this (check with the user if not sure)

## mcp**github**assign_copilot_to_issue

Assign Copilot to a specific issue in a GitHub repository

## mcp**github**create_and_submit_pull_request_review

Create and submit a review for a pull request without review comments

## mcp**github**create_branch

Create a new branch in a GitHub repository

## mcp**github**create_issue

Create a new issue in a GitHub repository

## mcp**github**create_or_update_file

Create or update a single file in a GitHub repository

## mcp**github**create_pending_pull_request_review

Create a pending review for a pull request

## mcp**github**create_pull_request

Create a new pull request in a GitHub repository

## mcp**github**create_repository

Create a new GitHub repository in your account

## mcp**github**delete_file

Delete a file from a GitHub repository

## mcp**github**delete_pending_pull_request_review

Delete the requester's latest pending pull request review

## mcp**github**fork_repository

Fork a GitHub repository to your account or specified organization

## mcp**github**get_code_scanning_alert

Get details of a specific code scanning alert in a GitHub repository

## mcp**github**get_commit

Get details for a commit from a GitHub repository

## mcp**github**get_file_contents

Get the contents of a file or directory from a GitHub repository

## mcp**github**get_issue

Get details of a specific issue in a GitHub repository

## mcp**github**get_issue_comments

Get comments for a specific issue in a GitHub repository

## mcp**github**get_me

Get details of the authenticated GitHub user

## mcp**github**get_pull_request

Get details of a specific pull request in a GitHub repository

## mcp**github**get_pull_request_comments

Get comments for a specific pull request

## mcp**github**get_pull_request_diff

Get the diff of a pull request

## mcp**github**get_pull_request_files

Get the files changed in a specific pull request

## mcp**github**get_pull_request_reviews

Get reviews for a specific pull request

## mcp**github**get_pull_request_status

Get the status of a specific pull request

## mcp**github**get_secret_scanning_alert

Get details of a specific secret scanning alert in a GitHub repository

## mcp**github**get_tag

Get details about a specific git tag in a GitHub repository

## mcp**github**list_branches

List branches in a GitHub repository

## mcp**github**list_code_scanning_alerts

List code scanning alerts in a GitHub repository

## mcp**github**list_commits

Get list of commits of a branch in a GitHub repository

## mcp**github**list_issues

List issues in a GitHub repository

## mcp**github**list_pull_requests

List pull requests in a GitHub repository

## mcp**github**list_tags

List git tags in a GitHub repository

## mcp**github**merge_pull_request

Merge a pull request in a GitHub repository

## mcp**github**push_files

Push multiple files to a GitHub repository in a single commit

## mcp**github**request_copilot_review

Request a GitHub Copilot code review for a pull request. Use this for automated feedback on pull requests, usually before requesting a human reviewer

## mcp**github**search_code

Search for code across GitHub repositories

## mcp**github**search_issues

Search for issues in GitHub repositories

## mcp**github**search_repositories

Search for GitHub repositories

## mcp**github**search_users

Search for GitHub users

## mcp**github**submit_pending_pull_request_review

Submit the requester's latest pending pull request review

## mcp**github**update_issue

Update an existing issue in a GitHub repository

## mcp**github**update_pull_request

Update an existing pull request in a GitHub repository

## mcp**github**update_pull_request_branch

Update the branch of a pull request with the latest changes from the base branch

## mcp**context7**resolve-library-id

Resolves a package/product name to a Context7-compatible library ID and returns a list of matching libraries

## mcp**context7**get-library-docs

Fetches up-to-date documentation for a library

## mcp**notion**search

Perform a search over notion and connected sources

## mcp**notion**fetch

Retrieves details about a Notion entity

## mcp**notion**create-pages

Creates one or more Notion pages with specified properties and content

## mcp**notion**update-page

Update a Notion page's properties or content

## mcp**notion**move-pages

Move one or more Notion pages or databases to a new parent

## mcp**notion**duplicate-page

Duplicate a Notion page

## mcp**notion**create-database

Creates a new Notion database with the specified properties

## mcp**notion**update-database

Update a Notion database's properties, name, description, or other attributes

## mcp**notion**create-comment

Add a comment to a page

## mcp**notion**get-comments

Get all comments of a page

## mcp**notion**get-users

List all users

## mcp**notion**get-self

Retrieve your token's bot user

## mcp**notion**get-user

Retrieve a user

## mcp**ide**getDiagnostics

Get language diagnostics from VS Code

## mcp**ide**executeCode

Execute python code in the Jupyter kernel for the current notebook file

## mcp**browseruse**browser_navigate

Navigate to a URL in the browser

## mcp**browseruse**browser_click

Click an element on the page by its index

## mcp**browseruse**browser_type

Type text into an input field

## mcp**browseruse**browser_get_state

Get the current state of the page including all interactive elements

## mcp**browseruse**browser_extract_content

Extract structured content from the current page based on a query

## mcp**browseruse**browser_scroll

Scroll the page

## mcp**browseruse**browser_go_back

Go back to the previous page

## mcp**browseruse**browser_list_tabs

List all open tabs

## mcp**browseruse**browser_switch_tab

Switch to a different tab

## mcp**browseruse**browser_close_tab

Close a tab

## mcp**browseruse**retry_with_browser_use_agent

Retry a task using the browser-use agent
