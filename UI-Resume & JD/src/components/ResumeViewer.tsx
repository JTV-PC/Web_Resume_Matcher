
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { FileText, Download, Maximize2 } from "lucide-react";
import { Button } from "@/components/ui/button";

const ResumeViewer = () => {
  const highlightedKeywords = [
    { word: "JavaScript", type: "match" },
    { word: "React", type: "match" },
    { word: "Node.js", type: "match" },
    { word: "Python", type: "missing" },
    { word: "Leadership", type: "match" },
    { word: "Team Management", type: "match" }
  ];

  const resumeContent = `
SARAH JOHNSON
Software Engineer

CONTACT INFORMATION
Email: sarah.johnson@email.com
Phone: +1 (555) 123-4567
Location: San Francisco, CA

EXPERIENCE

Senior Software Engineer | Tech Solutions Inc. | 2021 - Present
• Led a team of 5 developers in building scalable web applications using JavaScript and React
• Implemented modern frontend architectures resulting in 40% performance improvement
• Collaborated with cross-functional teams to deliver high-quality software solutions
• Mentored junior developers and conducted code reviews

Software Engineer | Innovation Labs | 2020 - 2021
• Developed full-stack applications using Node.js and React
• Participated in agile development processes and sprint planning
• Built RESTful APIs and integrated third-party services
• Maintained code quality through testing and documentation

EDUCATION
Master of Science in Computer Science | Stanford University | 2020
Bachelor of Science in Software Engineering | UC Berkeley | 2018

TECHNICAL SKILLS
• Frontend: JavaScript, React, TypeScript, HTML5, CSS3
• Backend: Node.js, Express.js, RESTful APIs
• Databases: PostgreSQL, MongoDB
• Tools: Git, Docker, AWS, Jenkins

SOFT SKILLS
• Leadership and team management
• Strong communication and collaboration abilities
• Problem-solving and analytical thinking
• Adaptability and continuous learning mindset

CERTIFICATIONS
• AWS Certified Developer Associate
• Scrum Master Certification
  `;

  return (
    <Card className="shadow-sm border border-gray-200 h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg text-gray-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-blue-600" />
            Resume Preview
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
            <Button variant="outline" size="sm">
              <Maximize2 className="w-4 h-4 mr-2" />
              Full View
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Keyword Legend */}
        <div className="flex flex-wrap gap-2 p-3 bg-gray-50 rounded-lg">
          <span className="text-sm font-medium text-gray-700">Keywords:</span>
          {highlightedKeywords.map((keyword, index) => (
            <Badge 
              key={index}
              variant="outline"
              className={
                keyword.type === "match" 
                  ? "bg-green-50 text-green-700 border-green-200" 
                  : "bg-red-50 text-red-700 border-red-200"
              }
            >
              {keyword.word}
              {keyword.type === "missing" && " (Missing)"}
            </Badge>
          ))}
        </div>

        {/* Resume Content */}
        <div className="bg-white border rounded-lg p-6 max-h-96 overflow-y-auto">
          <div className="whitespace-pre-line text-sm leading-relaxed text-gray-700">
            {resumeContent.split('\n').map((line, index) => {
              let processedLine = line;
              
              // Highlight keywords
              highlightedKeywords.forEach(keyword => {
                const regex = new RegExp(`\\b${keyword.word}\\b`, 'gi');
                if (keyword.type === "match") {
                  processedLine = processedLine.replace(
                    regex, 
                    `<mark class="bg-green-100 text-green-800 px-1 rounded">${keyword.word}</mark>`
                  );
                }
              });

              return (
                <div 
                  key={index}
                  dangerouslySetInnerHTML={{ __html: processedLine }}
                  className={
                    line.trim() === '' ? 'h-2' :
                    line.includes('SARAH JOHNSON') ? 'text-xl font-bold text-gray-900 mb-2' :
                    line.includes('Software Engineer') && !line.includes('|') ? 'text-lg text-blue-600 mb-4' :
                    line.includes('CONTACT') || line.includes('EXPERIENCE') || line.includes('EDUCATION') || line.includes('TECHNICAL') || line.includes('SOFT') || line.includes('CERTIFICATIONS') ? 'text-base font-semibold text-gray-900 mt-4 mb-2 border-b border-gray-200 pb-1' :
                    line.includes('|') ? 'font-medium text-gray-800 mt-3 mb-1' :
                    line.startsWith('•') ? 'ml-4' :
                    ''
                  }
                />
              );
            })}
          </div>
        </div>

        {/* Missing Skills Alert */}
        <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg">
          <div className="flex items-start gap-2">
            <div className="w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center mt-0.5">
              <span className="text-white text-xs font-bold">!</span>
            </div>
            <div>
              <p className="text-sm font-medium text-amber-800">Missing Required Skills</p>
              <p className="text-xs text-amber-700 mt-1">
                Candidate lacks Python experience which is required for this position.
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ResumeViewer;
