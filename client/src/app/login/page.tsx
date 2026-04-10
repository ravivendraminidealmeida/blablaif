'use client';

import { useState } from "react";
import { Button, Input, Card, CardBody, CardHeader, Link } from "@heroui/react";
import { fetchApi } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function Login() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: "", // FastAPI handles this as email under the hood for OAuth2 Form
    password: "",
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const urlEncodedParams = new URLSearchParams();
      urlEncodedParams.append("username", formData.username);
      urlEncodedParams.append("password", formData.password);

      const response = await fetchApi("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: urlEncodedParams,
      });

      // Save token securely
      localStorage.setItem("token", response.access_token);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Invalid credentials");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gradient-to-tr from-gray-900 to-gray-800">
      <Card className="max-w-sm w-full p-4 shadow-xl">
        <CardHeader className="flex flex-col items-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-teal-400 bg-clip-text text-transparent">BlaBlaIF</h1>
          <p className="text-sm text-default-500">Sign in to your account</p>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            {error && <p className="text-danger text-sm text-center">{error}</p>}
            
            <Input type="email" label="Email" name="username" value={formData.username} onChange={handleChange} required />
            <Input type="password" label="Password" name="password" value={formData.password} onChange={handleChange} required />
            
            <Button type="submit" color="primary" isLoading={isLoading} className="mt-2 font-semibold">
              Login
            </Button>
            
            <p className="text-center text-sm mt-4">
              Don't have an account? <Link href="/register" size="sm">Register here</Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}
