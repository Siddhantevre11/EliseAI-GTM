import { NextRequest, NextResponse } from "next/server";

const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || "http://localhost:8000";

export async function POST(request: Request) {
  const formData = await request.formData();
  const file = formData.get("file") as File;

  if (!file) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }

  // Forward to backend
  const backendFormData = new FormData();
  backendFormData.append("file", file);

  try {
    const response = await fetch(`${PYTHON_BACKEND_URL}/upload-leads`, {
      method: "POST",
      body: backendFormData,
    });

    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json({ error: data.detail || data.message }, { status: 400 });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Upload error:", error);
    return NextResponse.json(
      { error: "Upload failed. Please try again." },
      { status: 500 }
    );
  }
}