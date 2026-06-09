/**
 * @file mcdj.tsp
 * @description Provides domain model for mcdj app
 * @author 
 * @version 0.0.1
 * @copyright 2025 Continuum Software
 * @license MIT
 * See https://typespec.io/docs/language-basics/overview/
 */

// domain 
namespace RecordShop;

@valueObject
model Price {
  amount: float64;
  currency: string;
}

@entity
model Album {
  @key id: string;
  title: string;
  artist: string;
  price: Price;
  condition: "New" | "Used";
}

@aggregateRoot
model Order {
  @key id: string;
  customerId: string;
  items: Album[];
}

@entity
model User {
  @key id: string;
  username: string;
  email: string;
  // Note: In a real application, you'd never store plain text passwords
  // This is just for illustration
  passwordHash: string;
  // You might also want to add fields like:
  // createdAt: Date;
  // lastLogin: Date;
}

@aggregateRoot
model Order {
  @key id: string;
  userId: string; // Changed from customerId to userId for consistency
  items: Album[];
  // You might want to add:
  // createdAt: Date;
  // status: "Pending" | "Shipped" | "Delivered";
}
