
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { User, CheckCircle, FileText, Send } from "lucide-react";

const Approved = () => {
  const approvedCandidates = [
    {
      id: 1,
      name: "Alex Thompson",
      role: "Senior Developer",
      score: 89,
      maxScore: 94,
      approvedDate: "Nov 12, 2024",
      sentToHM: true
    },
    {
      id: 2,
      name: "Maria Garcia",
      role: "Data Scientist",
      score: 91,
      maxScore: 94,
      approvedDate: "Nov 11, 2024",
      sentToHM: true
    },
    {
      id: 3,
      name: "David Kim",
      role: "DevOps Engineer",
      score: 85,
      maxScore: 94,
      approvedDate: "Nov 10, 2024",
      sentToHM: false
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Approved Candidates</h1>
          <Badge variant="secondary" className="bg-green-100 text-green-700">
            {approvedCandidates.length} Approved
          </Badge>
        </div>

        <div className="grid gap-4">
          {approvedCandidates.map((candidate) => (
            <Card key={candidate.id} className="shadow-sm border border-gray-200">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                      <CheckCircle className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{candidate.name}</h3>
                      <p className="text-sm text-gray-500">{candidate.role}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-6">
                    <div className="text-center">
                      <div className="text-lg font-bold text-green-600">
                        {candidate.score}/{candidate.maxScore}
                      </div>
                      <p className="text-xs text-gray-500">Score</p>
                    </div>
                    
                    <div className="text-sm text-gray-500">
                      Approved: {candidate.approvedDate}
                    </div>
                    
                    <Badge 
                      variant={candidate.sentToHM ? 'default' : 'secondary'}
                      className={candidate.sentToHM ? 'bg-blue-100 text-blue-700' : 'bg-yellow-100 text-yellow-700'}
                    >
                      {candidate.sentToHM ? 'Sent to HM' : 'Pending Send'}
                    </Badge>
                    
                    <div className="flex gap-2">
                      <Button
                        onClick={() => window.location.href = '/evaluation'}
                        size="sm"
                        variant="outline"
                      >
                        <FileText className="w-4 h-4 mr-2" />
                        View
                      </Button>
                      
                      {!candidate.sentToHM && (
                        <Button
                          size="sm"
                          className="bg-blue-600 hover:bg-blue-700"
                        >
                          <Send className="w-4 h-4 mr-2" />
                          Send to HM
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Approved;
