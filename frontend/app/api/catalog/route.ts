import { NextResponse } from "next/server";
import fs from "fs/promises";
import path from "path";

export async function GET() {
  try {
    // Navigate from frontend/app/api/catalog/route.ts to backend/scraper/data/catalog.json
    const catalogPath = path.join(
      process.cwd(),
      "..",
      "backend",
      "data",
      "shl_product_catalog.json"
    );
    
    const fileContents = await fs.readFile(catalogPath, "utf-8");
    const catalog = JSON.parse(fileContents);
    
    return NextResponse.json(catalog);
  } catch (error) {
    console.error("Failed to read catalog:", error);
    return NextResponse.json({ error: "Failed to load catalog" }, { status: 500 });
  }
}
