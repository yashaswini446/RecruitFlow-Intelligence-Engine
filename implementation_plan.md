# Implementation Plan - Redesign Templates to Premium Modern Standards

This plan outlines the design upgrades for the RecruitFlow Intelligence Engine to make it look professional, modern, and standard-compliant, adhering to modern UI/UX design patterns (sleek dark mode, custom typography, status badges, clean tables, and responsive layouts).

## User Review Required

> [!IMPORTANT]
> The redesign will apply a modern dark mode design with Tailwind-like styling using vanilla CSS. It replaces the simple, high-contrast, bare-bones UI with a premium look (using Google Font `Plus Jakarta Sans` or `Inter`, smooth gradients, card layouts with shadow effects, and color-coded skill badges). No underlying logic or Flask routes will be modified.

## Proposed Changes

### Stylesheets

#### [MODIFY] [style.css](file:///c:/Users/Naksh/OneDrive/Desktop/proj1/static/style.css)
Rewrite the stylesheet to establish:
- **Color System**: CSS variables for slate-900 (background), slate-800/700 (cards), indigo/violet (brand gradients), emerald (success/matched), amber/rose (warnings/gaps).
- **Typography**: Import and apply the `Plus Jakarta Sans` Google Font.
- **Layouts**: Use modern flexbox and grid spacing with larger gaps and clean padding.
- **Interactions**: Add hover states, scaling, and transition animations for cards, tables, and buttons.
- **Elements**: 
  - Styled tables with rounded borders and hoverable rows.
  - Badge designs for tech vs. soft skills.
  - Interactive upload zone styling.
  - Progress bar improvements for match scores.

### Templates

#### [MODIFY] [base.html](file:///c:/Users/Naksh/OneDrive/Desktop/proj1/templates/base.html)
- Include Google Fonts `Plus Jakarta Sans` and SVG icons (Lucide/Heroicons equivalent).
- Polish the global navbar/header with a subtle gradient background and a professional brand logo layout.

#### [MODIFY] [index.html](file:///c:/Users/Naksh/OneDrive/Desktop/proj1/templates/index.html)
- Redesign forms to be clean, with highlighted input fields on focus.
- Convert simple tables to cards and modern tables with rounded headers and clear actions.
- Improve visual hierarchy of headings and numbers.

#### [MODIFY] [results.html](file:///c:/Users/Naksh/OneDrive/Desktop/proj1/templates/results.html)
- Style candidate match cards/table.
- Redesign match score progress bars with linear gradient fills.
- Format matched skills and gap lists with colored badges instead of plain text lists.

#### [MODIFY] [candidate_detail.html](file:///c:/Users/Naksh/OneDrive/Desktop/proj1/templates/candidate_detail.html)
- Enhance the candidate profile banner with contact details.
- Standardize the two-column grid.
- Style experience timeline blocks and education blocks.
- Build premium skill pills (Technical vs Soft) and AI recommendation charts/metrics.

## Verification Plan

### Automated/Local Verification
- Run the Flask development server on port 5001.
- Navigate through all pages (Dashboard, Job Matching Results, Candidate Details) to verify layout rendering and style consistency.
- Inspect responsive viewport scaling for desktop and mobile layouts.
