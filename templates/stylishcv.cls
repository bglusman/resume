%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Stylish Curriculum Vitae
% LaTeX Class
% Version 1.1 (September 10, 2021)
%
% This template originates from:
% https://www.LaTeXTemplates.com
%
% Authors:
% Stefano (https://www.kindoblue.nl)
% Vel (vel@LaTeXTemplates.com)
%
% License:
% CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{stylishcv}[2021/09/10 Stylish CV class v1.1]

\LoadClass[a4paper, oneside, final]{scrartcl}

\RequirePackage{scrlayer-scrpage}
\RequirePackage{titlesec}
\RequirePackage{marvosym}
\RequirePackage{tabularx,colortbl}
\RequirePackage{ebgaramond}
\RequirePackage{microtype}
\RequirePackage{hyperref}
\RequirePackage{xurl}
\RequirePackage{enumitem}

% Define custom commands for sections
\newcommand{\datedsubsection}[2]{%
  \subsection[#1]{#1 \hfill #2}%
}

\newcommand{\cvsubsection}[1]{%
  \subsection*{#1}%
}

% Section formatting
\titleformat{\section}{\large\scshape\raggedright}{}{0em}{}[\titlerule]
\titleformat{\subsection}{\normalsize\bfseries}{}{0em}{}

% Page setup
\addtolength{\voffset}{-0.5in}
\addtolength{\textheight}{3cm}

% Custom highlighting
\newcommand{\gray}{\rowcolor[gray]{.90}}

% Tight list definition
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}