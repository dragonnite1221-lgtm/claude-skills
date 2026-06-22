# ruff: noqa: F403, F405, E501, E402
import sys as _spsys
import pathlib as _sppath
_spsys.path.insert(0, str(_sppath.Path(__file__).resolve().parent))
from project_scaffolder_base import *  # noqa: F403,E402


def _mod_cg0_2():
    return {
        "requirements.txt": '''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.0
''',
        "alembic.ini": '''[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname
''',
        "index.ts": '''import express from "express";
import cors from "cors";
import helmet from "helmet";
import routes from "./routes";

const app = express();
const PORT = process.env.PORT || 8000;

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use("/api", routes);

app.get("/health", (_, res) => res.json({ status: "healthy" }));

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
''',
        "config.ts": '''export const config = {
  PORT: parseInt(process.env.PORT || "8000"),
  MONGODB_URI: process.env.MONGODB_URI || "mongodb://localhost:27017/app",
  JWT_SECRET: process.env.JWT_SECRET || "change-me",
};
''',
        "database.ts": '''import mongoose from "mongoose";
import { config } from "./config";

export async function connectDatabase(): Promise<void> {
  await mongoose.connect(config.MONGODB_URI);
  console.log("Connected to MongoDB");
}
''',
        "users.ts": '''import { Router } from "express";
const router = Router();

router.get("/", async (req, res) => {
  res.json({ users: [] });
});

router.post("/", async (req, res) => {
  res.status(201).json({ message: "User created" });
});

export default router;
''',
        "User.ts": '''import mongoose, { Schema, Document } from "mongoose";

export interface IUser extends Document {
  email: string;
  name?: string;
  createdAt: Date;
}

const userSchema = new Schema<IUser>({
  email: { type: String, required: true, unique: true },
  name: String,
}, { timestamps: true });

export const User = mongoose.model<IUser>("User", userSchema);
''',
        "auth.ts": '''import { Request, Response, NextFunction } from "express";

export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) return res.status(401).json({ error: "Authentication required" });
  // Verify token
  next();
}
''',
        "error.ts": '''import { Request, Response, NextFunction } from "express";

export function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  console.error(err.stack);
  res.status(500).json({ error: "Internal server error" });
}
''',
        "App.tsx": f'''function App() {{
  return (
    <div className="min-h-screen bg-gray-50">
      <main className="container mx-auto p-4">
        <h1 className="text-3xl font-bold">{project_name}</h1>
        <p className="mt-4 text-gray-600">Welcome to your new project.</p>
      </main>
    </div>
  );
}}
export default App;
''',
        "main.tsx": '''import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><App /></React.StrictMode>
);
''',
        "index.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;
''',
    }
