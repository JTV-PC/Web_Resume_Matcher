import { Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Users, FileText, CheckCircle, Send, MessageCircle } from "lucide-react";
import ResumeViewer from "@/components/ResumeViewer";
import { useEffect, useState } from "react";

import { BarChart3, AlertTriangle } from "lucide-react";

import { User, Mail, Phone, Building, Calendar } from "lucide-react";
import AppSidebar from "@/components/AppSidebar";

const Evaluation = () => {
  const sidebarItems = [
    { title: "Home", icon: Users, path: "/" },
    { title: "Under Review", icon: FileText, path: "/under-review" },
    { title: "Approved", icon: CheckCircle, path: "/approved" },
  ];

  const [selectedCandidate, setSelectedCandidate] = useState(null);


  useEffect(() => {
    const stored = localStorage.getItem("selectedCandidate");
    if (stored) {
      setSelectedCandidate(JSON.parse(stored));
    }
    
  }, []);

  if (!selectedCandidate || !selectedCandidate.candidate) {
    return <div>Loading candidate data...</div>; // Or a spinner
  }

  const candidate = selectedCandidate.candidate;

  const scoreData = [
    {
      category: "Technical Skills",
      score: candidate.technical_skills_score || 0,
      maxPoints: 50,
      notes: candidate.technical_skills || "No data",
      status: candidate.technical_skills_score >= 35 ? "good" : "warning"
    },
    {
      category: "Experience",
      score: candidate.experience_score || 0,
      maxPoints: 20,
      notes: candidate.experience || "No data",
      status: candidate.experience_score >= 15 ? "excellent" : "good"
    },
    {
      category: "Soft Skills",
      score: candidate.soft_skills_score || 0,
      maxPoints: 10,
      notes: candidate.soft_skills || "No data",
      status: candidate.soft_skills_score >= 6 ? "good" : "warning"
    },
    {
      category: "Education Level",
      score: candidate.education_score || 0,
      maxPoints: 10,
      notes: candidate.education || "No data",
      status: candidate.education_score >= 7 ? "excellent" : "good"
    },
    {
      category: "Certifications",
      score: candidate.certifications_score || 0,
      maxPoints: 10,
      notes: candidate.certifications || "No data",
      status: candidate.certifications_score >= 6 ? "excellent" : "good"
    }
  ];

  const totalScore = candidate.final_score || 0;
  const totalMaxPoints = scoreData.reduce((sum, item) => sum + item.maxPoints, 0);
  const overallPercentage = totalMaxPoints ? (totalScore / totalMaxPoints) * 100 : 0;



  const getStatusIcon = (status: string) => {
    switch (status) {
      case "warning":
        return <AlertTriangle className="w-4 h-4 text-amber-500" />;
      case "good":
      case "excellent":
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "warning":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "good":
        return "bg-blue-50 text-blue-700 border-blue-200";
      case "excellent":
        return "bg-green-50 text-green-700 border-green-200";
      default:
        return "bg-gray-50 text-gray-700 border-gray-200";
    }
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gray-50">
        {/* <Sidebar className="border-r bg-white">
          <SidebarContent>
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold text-blue-600">Candidate Compass</h2>
              <p className="text-sm text-gray-500">L&D Dashboard</p>
            </div>
            <SidebarGroup>
              <SidebarGroupLabel className="text-gray-700">Candidate Pipeline</SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {sidebarItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton 
                        className="hover:bg-blue-50 hover:text-blue-600 transition-colors"
                        onClick={() => window.location.href = item.path}
                      >
                        <item.icon className="w-4 h-4" />
                        <span>{item.title}</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar> */}
        <AppSidebar/>

        <main className="flex-1 p-6 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <SidebarTrigger className="lg:hidden" />
              <h1 className="text-2xl font-bold text-gray-900">Candidate Evaluation</h1>
            </div>
            <Badge variant="secondary" className="bg-blue-100 text-blue-700">
              Active Review
            </Badge>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - Candidate Info & Scores */}
            <div className="lg:col-span-1 space-y-6">
              {/* <CandidateCard /> */}
              <Card className="shadow-sm border border-gray-200">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg text-gray-900 flex items-center gap-2">
                    <User className="w-5 h-5 text-blue-600" />
                    Candidate Summary
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-blue-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{candidate.name}</h3>
                      <p className="text-sm text-gray-500"> {selectedCandidate.role}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">{candidate.email}</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">{candidate.contact_no}</span>
                    </div>
                    
                    {/* <div className="flex items-center gap-2 text-sm">
                      <Building className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">Tech Solutions Inc.</span>
                    </div> */}
                    
                    {/* <div className="flex items-center gap-2 text-sm">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">Resume uploaded: Nov 15, 2024</span>
                    </div> */}
                  </div>
                  
                  <div className="pt-2">
                    <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                      Active Candidate
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="shadow-sm border border-gray-200">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg text-gray-900 flex items-center gap-2">
                        <BarChart3 className="w-5 h-5 text-blue-600" />
                        Score Breakdown
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-semibold text-blue-900">Total Score</span>
                          <span className="text-xl font-bold text-blue-900">
                            {totalScore} / {totalMaxPoints}
                          </span>
                        </div>
                        <Progress value={overallPercentage} className="h-2" />
                        <p className="text-sm text-blue-700 mt-1">{overallPercentage.toFixed(0)}% Match</p>
                      </div>
              
                      <div className="space-y-3">
                        {scoreData.map((item, index) => (
                          <div key={index} className="p-3 border rounded-lg hover:bg-gray-50 transition-colors">
                            <div className="flex justify-between items-start mb-2">
                              <div className="flex items-center gap-2">
                                {getStatusIcon(item.status)}
                                <span className="font-medium text-gray-900">{item.category}</span>
                              </div>
                              <span className="font-semibold text-gray-700">
                                {item.score} / {item.maxPoints}
                              </span>
                            </div>
                            
                            <Progress 
                              value={(item.score / item.maxPoints) * 100} 
                              className="h-1.5 mb-2" 
                            />
                            
                            <div className="flex items-center justify-between">
                              <Badge variant="outline" className="text-xs text-green-700 border-green-300 bg-green-50">
                                 {item.notes?.split(',').slice(0, 4).join(', ')}
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {((item.score / item.maxPoints) * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>



              {/* <ScoreBreakdown /> */}
            </div>

            Right Column - Resume Viewer
            <div className="lg:col-span-2">
              <ResumeViewer />
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Evaluation;
