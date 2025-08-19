
## Entity Structure

```typescript
interface Customer {
  // identifiers //
  /** unique customer id */
  id: string;
  
  // properties //
  /** customer's email address */
  email: string;
  /** customer's first name */
  firstName: string;
  /** customer's last name */
  lastName: string;
  /** customer's date of birth */
  dateOfBirth: Date | null;
  
  // flags //
  /** current account status */
  status: 'active' | 'inactive';
  /** true if the customer is in the member club */
  isMember: boolean;
  
  // timestamps //
  /** creation timestamp (utc) */
  createdAt: Date;
  /** last update timestamp (utc) */
  updatedAt: Date;
  
  // relations //
  /** customer orders */
  orders?: Order[];
}
```

## Prisma Schema

```prisma
// file: prisma/models/customer.prisma

model Customer {
  // identifiers //
  id           String    @id @default(uuid())                /// unique customer id

  // properties //
  email        String    @unique                             /// customer's email address
  firstName    String    @map("first_name")                  /// customer's first name
  lastName     String    @map("last_name")                   /// customer's last name
  dateOfBirth  DateTime? @map("date_of_birth")               /// customer's date of birth

  // flags //
  status       CustomerStatus @default(active)               /// current account status
  isMember     Boolean   @default(true) @map("is_active")    /// true if the customer is in the member club

  // timestamps //
  createdAt    DateTime  @default(now()) @map("created_at")  /// creation timestamp (utc)
  updatedAt    DateTime  @updatedAt @map("updated_at")       /// last update timestamp (utc)

  // relations //
  orders       Order[]                                       /// customer orders

  // annotations //
  @@map("customers")

  // add @@index([...]) here if you frequently filter by fields (e.g., isActive, createdAt)
}

enum CustomerStatus {
  active    /// default state
  inactive  /// customer is no longer with us
}
```
