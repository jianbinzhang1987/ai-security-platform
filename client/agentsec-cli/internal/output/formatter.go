package output

import (
	"fmt"
	"sort"

	"github.com/fatih/color"
)

func PrintSuccess(msg string) {
	color.New(color.FgGreen).Printf("OK   %s\n", msg)
}

func PrintWarning(msg string) {
	color.New(color.FgYellow).Printf("WARN %s\n", msg)
}

func PrintError(msg string) {
	color.New(color.FgRed).Printf("ERR  %s\n", msg)
}

func PrintInfo(msg string) {
	fmt.Println(msg)
}

func PrintKV(key string, value any) {
	fmt.Printf("%-20s %v\n", key, value)
}

func PrintMap(payload map[string]any) {
	keys := make([]string, 0, len(payload))
	for key := range payload {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, key := range keys {
		PrintKV(key, payload[key])
	}
}
