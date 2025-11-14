import React, { useState } from 'react';
import { CheckCircle, XCircle, Award, Github, User, AlertCircle } from 'lucide-react';

export default function BootstrapAutoGrader() {
  const [studentName, setStudentName] = useState('');
  const [githubUsername, setGithubUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const requiredClasses = [
    'text-center',
    'text-primary',
    'fw-bold',
    'text-success',
    'text-danger',
    'text-warning',
    'text-info',
    'text-muted',
    'mb-4',
    'bg-primary',
    'text-white',
    'bg-success',
    'bg-danger',
    'bg-warning',
    'bg-dark',
    'text-light'
  ];

  const gradeSubmission = async () => {
    if (!studentName.trim() || !githubUsername.trim()) {
      alert('Please enter both your name and GitHub username!');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      // Construct GitHub raw content URL for index.html
      const githubUrl = `https://raw.githubusercontent.com/${githubUsername.trim()}/${githubUsername.trim()}.github.io/main/index.html`;
      
      const response = await fetch(githubUrl);
      
      if (!response.ok) {
        throw new Error('Could not fetch index.html from GitHub Pages repository');
      }

      const htmlContent = await response.text();
      
      // Check for required classes
      const foundClasses = [];
      const missingClasses = [];
      const suggestions = [];

      requiredClasses.forEach(className => {
        // Check if class exists in the HTML content
        const regex = new RegExp(`class=["'][^"']*\\b${className}\\b[^"']*["']`, 'g');
        if (regex.test(htmlContent)) {
          foundClasses.push(className);
        } else {
          missingClasses.push(className);
        }
      });

      // Calculate grade
      const grade = Math.round((foundClasses.length / requiredClasses.length) * 10);

      // Generate suggestions
      if (missingClasses.length > 0) {
        suggestions.push(`Missing ${missingClasses.length} required Bootstrap classes`);
        
        const missingText = missingClasses.filter(c => c.startsWith('text-'));
        const missingBg = missingClasses.filter(c => c.startsWith('bg-'));
        const missingUtility = missingClasses.filter(c => !c.startsWith('text-') && !c.startsWith('bg-'));

        if (missingText.length > 0) {
          suggestions.push(`Add text utility classes: ${missingText.join(', ')}`);
        }
        if (missingBg.length > 0) {
          suggestions.push(`Add background classes: ${missingBg.join(', ')}`);
        }
        if (missingUtility.length > 0) {
          suggestions.push(`Add utility classes: ${missingUtility.join(', ')}`);
        }
      }

      if (grade === 10) {
        suggestions.push('Perfect! All required Bootstrap classes are present! 🎉');
        suggestions.push('Consider adding more Bootstrap components for extra practice');
      } else if (grade >= 7) {
        suggestions.push('Great work! Just a few more classes needed');
      } else if (grade >= 5) {
        suggestions.push('Good start! Review Bootstrap documentation for missing classes');
      } else {
        suggestions.push('Keep practicing! Make sure to include all required Bootstrap utility classes');
      }

      setResult({
        grade,
        foundClasses,
        missingClasses,
        suggestions,
        totalRequired: requiredClasses.length
      });

    } catch (error) {
      alert(`Error: ${error.message}\n\nMake sure:\n1. Your GitHub username is correct\n2. You have a repository named ${githubUsername}.github.io\n3. There's an index.html file in the main branch\n4. The repository is public`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-indigo-900 mb-2">
            🎓 Mr Eyobed's Auto Grader
          </h1>
          <p className="text-xl text-indigo-700 italic font-medium">
            "Do things genuinely"
          </p>
          <p className="text-gray-600 mt-2">Bootstrap Class Checker</p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-xl p-8 mb-6">
          <div className="space-y-6">
            <div>
              <label className="flex items-center text-gray-700 font-semibold mb-2">
                <User className="w-5 h-5 mr-2 text-indigo-600" />
                Student Name
              </label>
              <input
                type="text"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                placeholder="Enter your full name"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none transition"
              />
            </div>

            <div>
              <label className="flex items-center text-gray-700 font-semibold mb-2">
                <Github className="w-5 h-5 mr-2 text-indigo-600" />
                GitHub Username
              </label>
              <input
                type="text"
                value={githubUsername}
                onChange={(e) => setGithubUsername(e.target.value)}
                placeholder="Enter your GitHub username"
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-indigo-500 focus:outline-none transition"
              />
              <p className="text-sm text-gray-500 mt-2">
                We'll check: https://github.com/{githubUsername || 'username'}/{githubUsername || 'username'}.github.io
              </p>
            </div>

            <button
              onClick={gradeSubmission}
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-lg transition transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Grading...
                </span>
              ) : (
                '📝 Submit for Grading'
              )}
            </button>
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className="bg-white rounded-lg shadow-xl p-8 animate-fade-in">
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-24 h-24 bg-indigo-100 rounded-full mb-4">
                <Award className="w-12 h-12 text-indigo-600" />
              </div>
              <h2 className="text-3xl font-bold text-gray-800 mb-2">
                {studentName}'s Results
              </h2>
              <div className="text-6xl font-bold text-indigo-600 mb-2">
                {result.grade}/10
              </div>
              <p className="text-gray-600">
                {result.foundClasses.length} out of {result.totalRequired} classes found
              </p>
            </div>

            {/* Progress Bar */}
            <div className="mb-8">
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-indigo-600 h-4 rounded-full transition-all duration-1000"
                  style={{ width: `${(result.grade / 10) * 100}%` }}
                />
              </div>
            </div>

            {/* Found Classes */}
            {result.foundClasses.length > 0 && (
              <div className="mb-6">
                <h3 className="flex items-center text-lg font-bold text-green-700 mb-3">
                  <CheckCircle className="w-5 h-5 mr-2" />
                  Found Classes ({result.foundClasses.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.foundClasses.map((cls, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium"
                    >
                      {cls}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Missing Classes */}
            {result.missingClasses.length > 0 && (
              <div className="mb-6">
                <h3 className="flex items-center text-lg font-bold text-red-700 mb-3">
                  <XCircle className="w-5 h-5 mr-2" />
                  Missing Classes ({result.missingClasses.length})
                </h3>
                <div className="flex flex-wrap gap-2">
                  {result.missingClasses.map((cls, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium"
                    >
                      {cls}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Suggestions */}
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
              <h3 className="flex items-center text-lg font-bold text-blue-900 mb-3">
                <AlertCircle className="w-5 h-5 mr-2" />
                Suggestions & Feedback
              </h3>
              <ul className="space-y-2">
                {result.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="text-blue-800 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="mt-6 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> Make sure your GitHub repository is public and named as username.github.io with an index.html file in the main branch.
          </p>
        </div>
      </div>
    </div>
  );
}