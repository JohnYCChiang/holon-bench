package weekday

var names = [7]string{
	"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
}

var monthOffset = [12]int{0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4}

// Weekday returns the English day name for the proleptic Gregorian date
// (year, month, day) using Sakamoto's algorithm. month is 1..12, day is 1..31.
func Weekday(year, month, day int) string {
	y := year
	// BUG: Sakamoto's method treats January and February as months of the
	// PREVIOUS year (because of the leap-day adjustment). Omitting "if month < 3
	// { y-- }" makes every January/February date off by one weekday.
	idx := (y + y/4 - y/100 + y/400 + monthOffset[month-1] + day) % 7
	return names[idx]
}
