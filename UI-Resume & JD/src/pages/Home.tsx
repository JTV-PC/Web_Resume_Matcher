import { SidebarProvider } from "@/components/ui/sidebar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, FileText, Users, CheckCircle } from "lucide-react";
import { useState } from "react";
import { toast } from "@/hooks/use-toast";
import AppSidebar from "@/components/AppSidebar";
import { useNavigate } from "react-router-dom";

const Home = () => {
  const [resumeFiles, setResumeFiles] = useState<File[]>([]);
  const [jobDescFile, setJobDescFile] = useState<File | null>(null);
  const navigate=useNavigate ();
  const sidebarItems = [
    { title: "Home", icon: Users, path: "/" },
    { title: "Under Review", icon: FileText, path: "/under-review" },
    { title: "Approved", icon: CheckCircle, path: "/approved" },
  ];

  const handleResumeUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      const uploaded = Array.from(files);
      setResumeFiles((prev) => [...prev, ...uploaded]);
 
      toast({
        title: "Resumes Uploaded",
        description: `${uploaded.length} file(s) uploaded successfully.`,
      });
    }
  };
 
  const handleJobDescUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setJobDescFile(file);
      toast({
        title: "Job Description Uploaded",
        description: `${file.name} has been uploaded successfully.`,
      });
    }
  };
 
  const handleMatch = async () => {
    if (resumeFiles.length === 0 || !jobDescFile) {
      toast({
        title: "Missing Files",
        description: "Please upload both resume(s) and job description to proceed.",
        variant: "destructive",
      });
      return;
    }
 
    toast({
      title: "Processing Match",
      description: "Analyzing resume(s) against job description...",
    });
 
    const formData = new FormData();
    formData.append("jd", jobDescFile);
    resumeFiles.forEach((file) => formData.append("resumes", file));
 
    try {
      const response = await fetch("http://localhost:8000/evaluate_batch", {
        method: "POST",
        body: formData,
      });
 
      const result = await response.json();
      console.log(result);
      navigate('/under-review')
      // Optionally handle result or navigate
    } catch (err) {
      console.error("Error uploading files:", err);
    }
  };

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-gray-50">
        <AppSidebar />

        <main className="flex-1 p-6">
          <div className="max-w-6xl mx-auto space-y-8">
            {/* Welcome Section */}
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold text-blue-600">Welcome L&D to Candidate Compass</h1>
              <p className="text-xl text-gray-600">Streamline your candidate evaluation process with AI-powered matching</p>
            </div>

            {/* Upload Section */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Resume Upload */}
              <Card className="shadow-sm border border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    Upload Resume
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600 mb-4">
                      Drag and drop a resume file or click to browse
                    </p>
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      multiple
                      onChange={handleResumeUpload}
                      className="hidden"
                      id="resume-upload"
                    />

                    <Button
                      onClick={() => document.getElementById('resume-upload')?.click()}
                      variant="outline"
                      className="border-blue-200 text-blue-600 hover:bg-blue-50"
                    >
                      Choose Files
                    </Button>
                  </div>
                  {resumeFiles.length > 0 && (
                    <div className="bg-green-50 border border-green-200 rounded p-3 space-y-1">
                      {resumeFiles.map((file, index) => (
                        <p key={index} className="text-sm text-green-700">
                          ✓ {file.name}
                        </p>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Job Description Upload */}
              <Card className="shadow-sm border border-gray-200">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-blue-600" />
                    Upload Job Description
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600 mb-4">
                      Drag and drop a job description or click to browse
                    </p>
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={handleJobDescUpload}
                      className="hidden"
                      id="jd-upload"
                    />
                    <Button
                      onClick={() => document.getElementById('jd-upload')?.click()}
                      variant="outline"
                      className="border-blue-200 text-blue-600 hover:bg-blue-50"
                    >
                      Choose File
                    </Button>
                  </div>
                  {jobDescFile && (
                    <div className="bg-green-50 border border-green-200 rounded p-3">
                      <p className="text-sm text-green-700">✓ {jobDescFile.name}</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Match Button */}
            <div className="text-center">
              <Button
                onClick={handleMatch}
                className="bg-blue-600 hover:bg-blue-700 px-8 py-3 text-lg"
                disabled={resumeFiles.length === 0 || !jobDescFile}
              >
                Start Candidate Evaluation
              </Button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <Card className="text-center">
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-blue-600">24</div>
                  <p className="text-gray-600">Candidates Today</p>
                </CardContent>
              </Card>
              <Card className="text-center">
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-green-600">18</div>
                  <p className="text-gray-600">Under Review</p>
                </CardContent>
              </Card>
              <Card className="text-center">
                <CardContent className="pt-6">
                  <div className="text-2xl font-bold text-purple-600">6</div>
                  <p className="text-gray-600">Approved</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
};

export default Home;
