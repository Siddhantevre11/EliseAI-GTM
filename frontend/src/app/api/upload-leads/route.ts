import { NextRequest, NextResponse } from "next/server";
import { PYTHON_BACKEND_URL } from "@/lib/backendConfig";

export async function POST(request: Request) {
  const endpoint = "upload-leads";
  console.log(`Proxying request to: ${PYTHON_BACKEND_URL}/${endpoint}`);

  const formData = await request.formData();
  const file = formData.get("file") as File;

  if (!file) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }

  const backendFormData = new FormData();
  backendFormData.append("file", file);

  try {
    const response = await fetch(`${PYTHON_BACKEND_URL}/${endpoint}`, {
      method: "POST",
      body: backendFormData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error [${endpoint}]:`, errorText);
      let errorMsg = "Service temporarily unavailable. Please try again.";
      try {
        const errJson = JSON.parse(errorText);
        if (errJson.detail) errorMsg = errJson.detail;
      } catch (e) {
        if (errorText) errorMsg = errorText;
      }
      return NextResponse.json(
        { error: errorMsg },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error(`Proxy error [${endpoint}]:`, error);
    return NextResponse.json(
      { error: "Service temporarily unavailable. Please try again." },
      { status: 502 }
    );
  }
}