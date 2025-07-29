# Service Design Patterns

## Table of Contents

- [Service Organization](#architecture) `architecture`
- [Data Operation Names](#operation_naming) `operation_naming`
- [API Patterns](#request_response) `request_response`
- [Error Patterns](#error_patterns) `error_patterns`
- [Authentication](#authentication) `authentication`

<architecture>

## Service Organization

```plaintext
services/      # Backend services
manifests/     # Operation specs
data/          # Data controllers
```

## Domain Alignment

Each service must have:

* Corresponding manifest defining operations
* Matching data controller for DB operations
* Clear domain boundaries

</architecture>

<operation_naming>

## Data Operation Names

* `get<Entity>` - Single entity
* `list<Entities>` - Multiple entities
* `set<Entity>` - Create/update
* `drop<Entity>` - Delete
* `search<Entities>` - Query

## Example

```typescript
export interface ProfileOperations {
  getUser: (id: string) => Promise<User>;
  listUsers: (filter?: UserFilter) => Promise<User[]>;
  setUser: (user: User) => Promise<User>;
  dropUser: (id: string) => Promise<void>;
  searchUsers: (query: string) => Promise<User[]>;
}
```

</operation_naming>

<request_response>

## API Patterns

```typescript
// Request with action context
export async function getProfile(
  userId: string,
  action: Action
): Promise<Profile> {
  action.log.info('fetching profile', { userId });
  // implementation
}

// Batch operations
export async function listProfiles(
  filter: ProfileFilter,
  action: Action
): Promise<Profile[]> {
  // implementation
}
```

## Response Format

* Single entity: Return entity or null
* List: Return array (empty if none)
* Mutations: Return updated entity
* Deletions: Return void

</request_response>

<error_patterns>

* `MissingDataError` - Entity not found
* `ValidationError` - Invalid input
* `ConflictError` - Duplicate/conflict
* `UnauthorizedError` - Access denied
</error_patterns>

<authentication>
* All operations receive `Action` context
* Auth checked at service boundary
* User context available via `action.user`
* Log all auth failures
</authentication>
