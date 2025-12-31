# Color Scheme Guide for QuantMetrics

## How to Change Colors

All colors are defined in `static/style.css` in the `:root` section (lines 7-48).

### Main Color Variables

#### Background Colors
- `--bg-primary`: Main background color (currently: `#0A0E27` - dark blue)
- `--bg-secondary`: Secondary background (currently: `#0F1729`)
- `--bg-card`: Card backgrounds (currently: `#1A1F3A`)
- `--bg-card-hover`: Card hover state (currently: `#1E2544`)

#### Text Colors
- `--text-primary`: Main text color (currently: `#FFFFFF` - white)
- `--text-secondary`: Secondary text (currently: `#94A3B8` - light gray)
- `--text-muted`: Muted text (currently: `#64748B` - gray)

#### Accent Colors (Currently Blue Theme)
- `--accent-blue-light`: `#60A5FA` - Light blue highlights
- `--accent-blue`: `#3B82F6` - Main blue accent
- `--accent-blue-dark`: `#2563EB` - Dark blue
- `--accent-cyan`: `#06B6D4` - Cyan accent
- `--accent-sky`: `#0EA5E9` - Sky blue
- `--accent-indigo`: `#6366F1` - Indigo

#### Functional Colors
- `--accent-green`: `#10B981` - Success/confirmation
- `--accent-yellow`: `#F59E0B` - Warning
- `--accent-red`: `#EF4444` - Error/alert

## Example Color Schemes

### 1. Green Theme (Trading/Finance)
```css
--accent-blue-light: #34D399;
--accent-blue: #10B981;
--accent-blue-dark: #059669;
--accent-cyan: #14B8A6;
--accent-sky: #2DD4BF;
--accent-indigo: #10B981;
```

### 2. Purple Theme (Premium)
```css
--accent-blue-light: #A78BFA;
--accent-blue: #8B5CF6;
--accent-blue-dark: #7C3AED;
--accent-cyan: #C084FC;
--accent-sky: #A855F7;
--accent-indigo: #8B5CF6;
```

### 3. Orange/Amber Theme (Energy)
```css
--accent-blue-light: #FBBF24;
--accent-blue: #F59E0B;
--accent-blue-dark: #D97706;
--accent-cyan: #FCD34D;
--accent-sky: #FBBF24;
--accent-indigo: #F59E0B;
```

### 4. Red Theme (Bold)
```css
--accent-blue-light: #F87171;
--accent-blue: #EF4444;
--accent-blue-dark: #DC2626;
--accent-cyan: #FB7185;
--accent-sky: #F87171;
--accent-indigo: #EF4444;
```

### 5. Light Theme (if you want to switch from dark)
```css
--bg-primary: #FFFFFF;
--bg-secondary: #F8F9FA;
--bg-card: #FFFFFF;
--bg-card-hover: #F1F3F5;
--text-primary: #1A1F3A;
--text-secondary: #475569;
--text-muted: #64748B;
--border-color: rgba(0, 0, 0, 0.1);
```

## Quick Steps to Change Colors

1. Open `static/style.css`
2. Find the `:root` section (lines 7-48)
3. Replace the color values with your desired colors
4. Save the file
5. Refresh your browser to see changes

## Tips

- Use a color picker tool to find hex codes
- Keep contrast ratios in mind for readability
- Test your changes in different sections of the app
- The shadow glow colors also use these accent colors, so they'll update automatically

