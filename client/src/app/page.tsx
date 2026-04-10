'use client';

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { fetchApi } from "@/lib/api";
import { Button, Card, CardBody, Spinner, Navbar, NavbarBrand, NavbarContent, NavbarItem } from "@heroui/react";

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }

    const fetchUser = async () => {
      try {
        const data = await fetchApi("/auth/me");
        setUser(data);
      } catch (err) {
        console.error("Authentication failed", err);
        localStorage.removeItem("token");
        router.push("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-900">
        <Spinner size="lg" color="primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-foreground">
      <Navbar isBordered className="bg-gray-900/50 backdrop-blur-md">
        <NavbarBrand>
          <p className="font-bold text-inherit bg-gradient-to-r from-blue-500 to-teal-400 bg-clip-text text-transparent text-xl">
            BlaBlaIF
          </p>
        </NavbarBrand>
        <NavbarContent justify="end">
          <NavbarItem>
            <Button color="danger" variant="flat" onPress={handleLogout}>
              Log Out
            </Button>
          </NavbarItem>
        </NavbarContent>
      </Navbar>

      <main className="container mx-auto p-4 md:p-8 flex flex-col gap-6 mt-8">
        <Card className="bg-gray-800 shadow-xl border-none">
          <CardBody className="p-8">
            <h1 className="text-4xl font-bold mb-2">Welcome back, {user?.name}!</h1>
            <p className="text-gray-400">
              You are signed in as a <strong className="text-teal-400">{user?.role}</strong> from College #{user?.college_id}.
            </p>
          </CardBody>
        </Card>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <Card className="bg-gradient-to-br from-blue-900/40 to-purple-900/40 border border-white/10 hover:scale-[1.02] transition-transform">
            <CardBody className="p-6">
              <h3 className="text-xl font-bold text-blue-300">Offer a Ride</h3>
              <p className="text-gray-400 mt-2 text-sm">Create a new carpool schedule and define your pickup points for other students.</p>
              <Button color="primary" className="mt-4 w-fit">Create Ride</Button>
            </CardBody>
          </Card>
          
          <Card className="bg-gradient-to-br from-teal-900/40 to-green-900/40 border border-white/10 hover:scale-[1.02] transition-transform">
            <CardBody className="p-6">
              <h3 className="text-xl font-bold text-teal-300">Find a Ride</h3>
              <p className="text-gray-400 mt-2 text-sm">Browse available carpoools matching your campus schedules and secure your seat.</p>
              <Button className="mt-4 w-fit bg-teal-500 text-white">Search Rides</Button>
            </CardBody>
          </Card>
        </div>
      </main>
    </div>
  );
}
