export const SUBJECTS = [
  'Physics',
  'Chemistry',
  'Biology',
  'Math',
  'Bangla',
  'English',
  'History',
  'Geography',
  'Philosophy',
  'Literature',
  'Social Science',
  'Religion',
] as const

export type Subject = (typeof SUBJECTS)[number]

export const SUBJECT_ICONS: Record<Subject, string> = {
  Physics: '⚛️',
  Chemistry: '🧪',
  Biology: '🧬',
  Math: '📐',
  Bangla: '🅱️',
  English: '📖',
  History: '🏛️',
  Geography: '🌍',
  Philosophy: '🧠',
  Literature: '✍️',
  'Social Science': '🤝',
  Religion: '🕌',
}

export const SUBJECT_COLORS: Record<Subject, string> = {
  Physics: '#7c6af7',
  Chemistry: '#f76a6a',
  Biology: '#4ade80',
  Math: '#facc15',
  Bangla: '#fb923c',
  English: '#38bdf8',
  History: '#c084fc',
  Geography: '#34d399',
  Philosophy: '#a78bfa',
  Literature: '#f472b6',
  'Social Science': '#60a5fa',
  Religion: '#fbbf24',
}
