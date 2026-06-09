import "@typespec/http";

using TypeSpec.Http;

namespace RecordShop;

model Price {
  amount: float64;
  currency: string;
}

model Album {
  @key id: string;
  title: string;
  artist: string;
  price: Price;
  condition: "New" | "Used";
}

model Order {
  @key id: string;
  userId: string;
  items: Album[];
  createdAt: string;
  status: "Pending" | "Shipped" | "Delivered";
}

model User {
  @key id: string;
  username: string;
  email: string;
  passwordHash: string;
  createdAt: string;
  lastLogin: string;
}

// API Operations
@route("/albums")
@tag("Albums")
interface Albums {
  @get
  listAlbums(): Album[];

  @get
  @route("/{id}")
  getAlbum(id: string): Album;

  @post
  createAlbum(album: Album): Album;

  @put
  @route("/{id}")
  updateAlbum(id: string, album: Album): Album;

  @delete
  @route("/{id}")
  deleteAlbum(id: string): void;
}

@route("/orders")
@tag("Orders")
interface Orders {
  @get
  listOrders(): Order[];

  @get
  @route("/{id}")
  getOrder(id: string): Order;

  @post
  createOrder(order: Order): Order;

  @put
  @route("/{id}")
  updateOrder(id: string, order: Order): Order;
}

@route("/users")
@tag("Users")
interface Users {
  @get
  listUsers(): User[];

  @get
  @route("/{id}")
  getUser(id: string): User;

  @post
  createUser(user: User): User;

  @put
  @route("/{id}")
  updateUser(id: string, user: User): User;

  @delete
  @route("/{id}")
  deleteUser(id: string): void;
}