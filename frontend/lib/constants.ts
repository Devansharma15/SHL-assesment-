/* Application constants. */

export const APP_NAME = "SHL Assessment Advisor";
export const APP_DESCRIPTION =
  "AI-powered assessment recommendations for HR professionals and recruiters.";

export const MAX_TURNS = 8;
export const MAX_MESSAGE_LENGTH = 5000;

export const EXAMPLE_PROMPTS = [
  {
    title: "Java Developer",
    prompt: "I need to assess candidates for a senior Java developer position",
    icon: "💻",
  },
  {
    title: "Sales Manager",
    prompt: "Looking for personality and leadership assessments for a sales management role",
    icon: "📊",
  },
  {
    title: "Customer Service",
    prompt: "Need to evaluate customer service representatives for a call center",
    icon: "🎧",
  },
  {
    title: "Graduate Program",
    prompt: "Setting up assessments for our graduate hiring program with 200 candidates",
    icon: "🎓",
  },
  {
    title: "Data Scientist",
    prompt: "Assessing mid-level data scientists — need Python, SQL, and analytical skills",
    icon: "📈",
  },
  {
    title: "Remote Workers",
    prompt: "We're hiring remote employees and want to assess their ability to work independently",
    icon: "🏠",
  },
];

export const WELCOME_MESSAGE =
  "Welcome! I'm your SHL Assessment Advisor. I can help you find the right assessments for your hiring needs. Tell me about the role you're hiring for, and I'll recommend the best SHL assessments.";

export const TEST_TYPE_COLORS: Record<string, string> = {
  "Cognitive Ability": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  "Personality Assessment": "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
  "Behavioral Assessment": "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
  "Skills Simulation": "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300",
  "Knowledge Test": "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300",
  "Skills Test": "bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300",
  "Language Assessment": "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300",
  Interview: "bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300",
  "Multi-Measure": "bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300",
};

export const TEST_TYPE_ICONS: Record<string, string> = {
  "Cognitive Ability": "🧠",
  "Personality Assessment": "🎭",
  "Behavioral Assessment": "🎯",
  "Skills Simulation": "💻",
  "Knowledge Test": "📚",
  "Skills Test": "⚡",
  "Language Assessment": "🌍",
  Interview: "🎙️",
  "Multi-Measure": "📋",
};
