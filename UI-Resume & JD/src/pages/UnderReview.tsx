
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { User, Clock, FileText } from "lucide-react";
import { useState,useEffect } from "react";
import { SidebarProvider } from "@/components/ui/sidebar";
import AppSidebar from "@/components/AppSidebar";

const UnderReview = () => {
  
  const [candidates, setCandidates] = useState([]);
  localStorage.removeItem("selectedCandidate");

  useEffect(() => {
    const fetchCandidates = async () => {
      try {
        const response = await fetch("http://localhost:8000/get_resume_delta/");
        if (!response.ok) throw new Error("Network response was not ok");

        const data = await response.json();

        const mappedData = data.map((candidate, index) => ({
          id: candidate.id,
          name: candidate.name,
          role: candidate.experience || "Not specified",
          score: candidate.final_score || 0,
          maxScore: 100, // optionally adjust if needed
          uploadDate: new Date().toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric"
          }),
          candidate:candidate,
          status: "pending" // hardcoded or derive from backend if available
        }));

        setCandidates(mappedData);
      } catch (error) {
        console.error("Failed to fetch candidate data:", error);
      }
    };

    fetchCandidates();
  }, []);


  return (
   <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gray-50">
        <AppSidebar />

        <main className="flex-1 p-6">
          <div className="max-w-6xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
              <h1 className="text-2xl font-bold text-gray-900">Candidates Under Review</h1>
              <Badge variant="secondary" className="bg-yellow-100 text-yellow-700">
                {candidates.length} Pending
              </Badge>
            </div>

            <div className="grid gap-4">
              {candidates.map((candidate) => (
                <Card key={candidate.id} className="shadow-sm border border-gray-200">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                          <User className="w-6 h-6 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{candidate.name}</h3>
                          <p className="text-sm text-gray-500">{candidate.role}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="text-lg font-bold text-blue-600">
                            {candidate.score}
                          </div>
                          <p className="text-xs text-gray-500">Score</p>
                        </div>
                        
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <Clock className="w-4 h-4" />
                          {candidate.uploadDate}
                        </div>
                        
                        <Badge 
                          variant={candidate.status === 'in-review' ? 'default' : 'secondary'}
                          className={candidate.status === 'in-review' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}
                        >
                          {candidate.status === 'in-review' ? 'In Review' : 'Pending'}
                        </Badge>
                        
                        <Button
                          onClick={() => {
                            localStorage.setItem("selectedCandidate", JSON.stringify(candidate));
                            window.location.href = "/evaluation#resume";
                          }}
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          <FileText className="w-4 h-4 mr-2" />
                          Review
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default UnderReview;
