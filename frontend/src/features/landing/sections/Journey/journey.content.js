import {
  UploadCloud,
  Brain,
  FileText,
  UserCheck,
  Search,
  Trophy,
} from "lucide-react";

export const journeyContent = {
  eyebrow: "ATHLETE JOURNEY",

  title: "From Upload To Opportunity.",

  description:
    "Shakti Sports AI turns a single performance video into a structured discovery pathway for athletes, coaches and scouts.",

  steps: [
    {
      icon: UploadCloud,
      title: "Upload",
      description: "Athlete uploads a short performance video.",
    },
    {
      icon: Brain,
      title: "AI Analysis",
      description: "Movement, technique and performance signals are analyzed.",
    },
    {
      icon: FileText,
      title: "Report",
      description: "A structured AI-assisted performance report is generated.",
    },
    {
      icon: UserCheck,
      title: "Coach Review",
      description: "Coaches can evaluate athletes using objective insights.",
    },
    {
      icon: Search,
      title: "Scout Match",
      description: "Scouts discover athletes based on event, region and score.",
    },
    {
      icon: Trophy,
      title: "Opportunity",
      description: "Athletes receive real pathways to training and trials.",
    },
  ],
};