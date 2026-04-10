'use client';

import { useState } from "react";
import { Button, Input, Card, CardBody, CardHeader, Link, Select, SelectItem } from "@heroui/react";
import { fetchApi } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function Register() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    role: "Student",
    college_id: 1, // Fixed to 1 as per current DB seeding
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      await fetchApi("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          ...formData,
          college_id: Number(formData.college_id),
        }),
      });
      router.push("/login");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gradient-to-tr from-gray-900 to-gray-800">
      <Card className="max-w-md w-full p-4 shadow-xl">
        <CardHeader className="flex flex-col items-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-500 to-teal-400 bg-clip-text text-transparent">BlaBlaIF</h1>
          <p className="text-sm text-default-500">Create your account</p>
        </CardHeader>
        <CardBody>
          <form onSubmit={handleRegister} className="flex flex-col gap-4">
            {error && <p className="text-danger text-sm text-center">{error}</p>}
            
            <Input label="Full Name" name="name" value={formData.name} onChange={handleChange} required />
            <Input type="email" label="Email" name="email" value={formData.email} onChange={handleChange} required />
            <Input label="Phone Number" name="phone" value={formData.phone} onChange={handleChange} required />
            
            <Select 
              label="Role" 
              name="role" 
              selectedKeys={[formData.role]}
              onChange={handleChange}
            >
              <SelectItem key="Student" value="Student">Student</SelectItem>
              <SelectItem key="Professor" value="Professor">Professor</SelectItem>
            </Select>

            <Input type="password" label="Password" name="password" value={formData.password} onChange={handleChange} required />
            
            <Button type="submit" color="primary" isLoading={isLoading} className="mt-4 font-semibold">
              Sign Up
            </Button>
            
            <p className="text-center text-sm mt-4">
              Already have an account? <Link href="/login" size="sm">Login here</Link>
            </p>
          </form>
        </CardBody>
      </Card>
    </div>
  );
}
