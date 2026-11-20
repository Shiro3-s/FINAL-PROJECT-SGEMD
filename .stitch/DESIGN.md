---
name: SGEMD Institutional Blue
colors:
  surface: '#ffffff'
  surface-dim: '#f7f8fa'
  surface-container: '#ffffff'
  on-surface: '#051533'
  on-surface-variant: '#162644'
  outline: '#bbbbbb'
  primary: '#004a93'
  on-primary: '#ffffff'
  primary-container: '#162644'
  secondary: '#ffd300'
  on-secondary: '#051533'
  error: '#051533'
  background: '#ffffff'
typography:
  display:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  heading:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 26px
  body:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
  label:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
rounded:
  sm: 8px
  md: 12px
  full: 999px
spacing:
  unit: 8px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 32px
  xl: 40px
---

# Design System: SGEMD

## 1. Visual Theme & Atmosphere

SGEMD is an institutional administration platform with a cool, high-contrast
blue-and-white interface. The visual language is structured, dependable, and
information-dense without becoming visually heavy: a dark navy shell anchors
the screen while white cards, blue links, and yellow highlights guide attention.

The design favors clear hierarchy over decoration. Borders, compact spacing,
sticky table headers, and restrained shadows make operational data easy to
scan. Yellow is reserved for emphasis and status attention; it is never used
as body text on white.

## 2. Color Palette & Roles

### Primary Foundation

- **White `#ffffff`** — page, card, table, and form surfaces.
- **Night navy `#051533`** — shell, header, primary text, and destructive-action
  buttons.
- **Deep blue `#162644`** — table headers, secondary text, and intermediate
  surfaces.

### Accent & Interactive

- **Institutional blue `#004a93`** — links, active navigation, primary actions,
  progress values, focus borders, and interactive icons.
- **Institutional yellow `#ffd300`** — active badges, counters, attention
  indicators, and accent actions with navy text.

### Typography & Text Hierarchy

- **Border gray `#bbbbbb`** — borders, separators, disabled controls, and
  non-text UI structure.
- Primary text uses `#051533`; supporting text uses `#162644`.

### Functional States

States use the same brand palette with an icon and text label: blue for active
or assigned, yellow for attention or pending, and white/gray bordered badges
for neutral or unassigned states. Red, green, and orange status colors are not
used.

## 3. Typography Rules

### Hierarchy & Weights

The interface uses **Inter** throughout. Page titles are 28px/700, card titles
are 16px/600, body copy is 14px/400, and labels are 13px/600. Metric values
use a 32px/800 treatment with tight tracking.

### Spacing Principles

Spacing follows an 8px rhythm with common steps of 8, 16, 20, 24, 32, and
40px. Form labels sit directly above fields; cards use 20px internal padding;
major sections use 20–28px vertical separation.

## 4. Component Stylings

### Buttons

Buttons are 40px high with 8px corners, 18px horizontal padding, Inter 14px
semibold text, and an icon placed before the label. Primary buttons use
`#004a93`; secondary buttons use white with a gray border; accent buttons use
`#ffd300` with navy text.

### Cards & Tables

Cards are white, bordered with `#bbbbbb`, rounded 12px, and use a subtle
`0 1px 2px rgba(5,21,51,.06)` shadow. Tables use deep-blue uppercase headers,
12–16px cell padding, gray row separators, optional alternating rows, sticky
headers, horizontal overflow on narrow screens, and a right-aligned action
column.

### Navigation

The desktop layout uses a 264px sticky navy sidebar and a 72px navy top bar.
Navigation labels are uppercase and slightly tracked; active links use
institutional blue. Below 1024px the sidebar becomes a drawer controlled by a
menu button.

### Inputs & Forms

Inputs and selects are 40px high, white, gray-bordered, and rounded 8px.
Focused fields use an institutional-blue border and a translucent blue halo.
Labels are visible above every field.

### Domain-Specific Components

Administrative metric cards combine a blue-tinted icon tile, a compact label,
large numeric value, and a six-pixel progress bar. Assignment tables combine
student email, project name, current teacher, status badge, and an icon-only
assign/reassign action.

## 5. Layout Principles

### Grid & Structure

Content is centered within a 1440px maximum width and uses CSS Grid cards:
four columns on wide screens, two below 1280px, and one below 768px.

### Whitespace Strategy

The sidebar and top bar remain visually strong while content uses generous
white space between the page header, callouts, metric cards, filters, and
tables. Tables remain dense internally for operational scanning.

### Alignment & Visual Balance

Page titles and explanatory copy are left aligned. Header actions sit to the
right. Numerical metrics are prominent; action controls remain at the far
right of each table row.

### Responsive Behavior & Touch

At 1024px the sidebar becomes a drawer; at 768px grids collapse to one column
and tables switch to stacked row cards. Interactive targets remain at least
32–40px and preserve visible focus states.

## 6. Design System Notes for Stitch Generation

### Language to Use

Describe screens as institutional, operational, high-contrast, structured,
blue-and-white dashboards with restrained yellow emphasis, compact data tables,
sticky navigation, and clear administrative hierarchy.

### Color References

Use only `#051533`, `#162644`, `#004a93`, `#ffd300`, `#ffffff`, and `#bbbbbb`,
plus translucent variants derived from those tokens.

### Component Prompts

- “Create a SGEMD administrator dashboard with a 264px navy sidebar, 72px
  navy top bar, white content canvas, blue active navigation, and yellow
  attention badges.”
- “Create a dense assignment-management card with labeled search fields,
  deep-blue sticky table headers, email/project columns, icon status badges,
  and right-aligned blue outline actions.”

### Incremental Iteration

Preserve the shell, logo, typography, palette, table density, and 8px spacing
rhythm first. Then adjust only the page-specific data, metrics, and actions;
do not introduce new colors, gradients, glass effects, or unrelated layouts.
