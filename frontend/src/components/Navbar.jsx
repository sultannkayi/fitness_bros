import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div style={{ padding: "10px", borderBottom: "1px solid #ccc" }}>
      <Link to="/" style={{ marginRight: "10px" }}>
        Home
      </Link>
      <Link to="/classes" style={{ marginRight: "10px" }}>
        Classes
      </Link>
      <Link to="/reservations">
        Reservations
      </Link>
    </div>
  );
}
