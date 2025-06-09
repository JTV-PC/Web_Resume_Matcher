import { Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar";
import { Users, FileText, CheckCircle } from "lucide-react";

const AppSidebar = () => {
  const sidebarItems = [
    { title: "Home", icon: Users, path: "/" },
    { title: "Under Review", icon: FileText, path: "/under-review" },
    { title: "Approved", icon: CheckCircle, path: "/approved" },
  ];

  return (
    <Sidebar className="border-r bg-white w-16" collapsible="none">
      <SidebarContent>
        <div className="p-4 border-b flex justify-center">
          <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center">
            <span className="text-white font-bold text-sm">CC</span>
          </div>
        </div>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {sidebarItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    className="hover:bg-blue-50 hover:text-blue-600 transition-colors justify-center"
                    onClick={() => window.location.href = item.path}
                    tooltip={item.title}
                  >
                    <item.icon className="w-5 h-5" />
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
};

export default AppSidebar;