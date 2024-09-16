package main

import (
	"fmt"
	"log"
	"math"
	"math/rand"
	"os"
	"strconv"

	"image/color"
	_ "image/jpeg"
	_ "image/png"

	"github.com/hajimehoshi/ebiten/v2"
	"github.com/hajimehoshi/ebiten/v2/ebitenutil"
	"github.com/hajimehoshi/ebiten/v2/vector"
)

var (
	bgImage         *ebiten.Image
	fishImage       *ebiten.Image
	WINDOW_WIDTH    = 1920
	WINDOW_HEIGHT   = 1080
	TIME_MULTIPLIER = 1.0
	MAX_FOOD        = 30
	avgSpeed        = 0.0 // Do not change that
	avgVision       = 0.0 // Do not change that
	avgHealth       = 0.0 // Do not change that
)

const (
	FISH_SIZE      = 20
	INITIAL_FISHES = 10
)

type Fish struct {
	imageWidth       int
	imageHeight      int
	x                float64
	y                float64
	vx               float64
	vy               float64
	speed            float64
	vision           float64
	health           float64
	age              float64
	canReproduce     bool
	lastReproduction float64
}

type Food struct {
	x          float64
	y          float64
	healthGain float64
}

type Fishes struct {
	fishes []*Fish
	num    int
}

type Game struct {
	fishes Fishes
	foods  []*Food
	op     ebiten.DrawImageOptions
}

func (g *Game) drawCircle(screen *ebiten.Image, x, y, radius int, clr color.Color) {
	radius64 := float64(radius)
	minAngle := math.Acos(1 - 1/radius64)
	for angle := float64(0); angle <= 360; angle += minAngle {
		xDelta := radius64 * math.Cos(angle)
		yDelta := radius64 * math.Sin(angle)
		x1 := int(math.Round(float64(x) + xDelta))
		y1 := int(math.Round(float64(y) + yDelta))
		screen.Set(x1, y1, clr)
	}
}

func init() {
	// load image fond.jpg
	img, _, err := ebitenutil.NewImageFromFile("fond.jpg")

	if err != nil {
		log.Fatal(err)
	}
	bgImage = img

	fishSprite, _, err := ebitenutil.NewImageFromFile("poisson.png")

	if err != nil {
		log.Fatal(err)
	}

	fishImage = fishSprite
}

func (g *Game) Update() error {
	g.CalculateAvgValues()
	for _, fish := range g.fishes.fishes {
		fish.x += fish.vx
		fish.y += fish.vy
		fish.OutOfBoundsDetection()
		fish.LifeTick(g)
		// Have 1/2000 chance of changing direction
		if rand.Intn(2000) == 0 {
			fish.RandDirectionAndSpeed()
		}

	}
	if len(g.foods) < MAX_FOOD {
		// Have 1/1000 chance of generating food
		if rand.Intn(1000) == 0 {
			g.GenerateFood()
		}
	}
	return nil
}

func (g *Game) GenerateFish() {
	x, y := rand.Float64()*float64(WINDOW_WIDTH-FISH_SIZE), rand.Float64()*float64(WINDOW_HEIGHT-FISH_SIZE)
	rspeed := rand.Float64() + 0.1
	rvision := rand.Float64() * 100
	g.fishes.fishes = append(g.fishes.fishes, &Fish{imageWidth: FISH_SIZE, imageHeight: FISH_SIZE, x: x, y: y, vx: 0, vy: 0, speed: rspeed, vision: rvision, lastReproduction: math.Floor(rand.Float64() * 10), health: 90 + math.Floor(rand.Float64()*10), age: math.Floor(rand.Float64() * 10)})
	g.fishes.fishes[len(g.fishes.fishes)-1].RandDirectionAndSpeed()
}

func (g *Game) CalculateAvgValues() {
	avgSpeed = 0
	avgHealth = 0
	avgVision = 0
	for _, fish := range g.fishes.fishes {
		avgSpeed += fish.speed
		avgHealth += fish.health
		avgVision += fish.vision
	}
	avgSpeed /= float64(len(g.fishes.fishes))
	avgHealth /= float64(len(g.fishes.fishes))
	avgVision /= float64(len(g.fishes.fishes))
}

func (g *Game) GenerateFood() {
	x, y := rand.Float64()*float64(WINDOW_WIDTH-FISH_SIZE), rand.Float64()*float64(WINDOW_HEIGHT-FISH_SIZE)
	healthGain := rand.Float64()*9 + 1
	g.foods = append(g.foods, &Food{x: x, y: y, healthGain: healthGain})
}

func (g *Game) Draw(screen *ebiten.Image) {

	screen.DrawImage(bgImage, nil)

	ebitenutil.DebugPrint(screen, fmt.Sprintf("FPS: %0.2f\nTPS: %0.2f\nFishes: %d\nFood: %d\nAvg speed: %0.2f\nAvg vision: %0.2f\nAvg health: %0.2f", ebiten.ActualFPS(), ebiten.ActualTPS(), len(g.fishes.fishes), len(g.foods), avgSpeed, avgVision, avgHealth))

	if len(g.fishes.fishes) == 0 {
		// No fishes generated yet, generate the initial batch
		for range INITIAL_FISHES {
			g.GenerateFish()
		}
	}

	for _, fish := range g.fishes.fishes {
		g.op.GeoM.Reset()
		if fish.vx > 0 {
			g.op.GeoM.Scale(-1, 1)
		}
		g.op.GeoM.Translate(fish.x, fish.y)
		screen.DrawImage(fishImage, &g.op)
		circlex := fish.x + FISH_SIZE/2
		if fish.vx > 0 {
			circlex = fish.x - FISH_SIZE/2
		}
		circleColor := color.RGBA{255, 255, 255, 255}
		if fish.canReproduce {
			circleColor = color.RGBA{0, 255, 0, 255}
		}
		g.drawCircle(screen, int(circlex), int(fish.y+FISH_SIZE/2), int(fish.vision), circleColor)
		ebitenutil.DebugPrintAt(screen, fmt.Sprintf("x: %0.2f\ny: %0.2f\nvx: %0.2f\nvy: %0.2f\nspeed: %0.2f\nvision: %0.2f\nhealth: %0.2f\nage: %0.2f\ncanReproduce: %t\nlastReproduction: %0.2f", fish.x, fish.y, fish.vx, fish.vy, fish.speed, fish.vision, fish.health, fish.age, fish.canReproduce, fish.lastReproduction), int(fish.x), int(fish.y+FISH_SIZE))
		for _, food := range fish.NearbyFood(g) {
			vector.StrokeLine(screen, float32(fish.x), float32(fish.y), float32(food.x), float32(food.y), 2, color.RGBA{255, 0, 0, 0}, false)
		}
	}

	for _, food := range g.foods {
		vector.DrawFilledCircle(screen, float32(food.x), float32(food.y), 5, color.RGBA{255, 255, 0, 255}, false)
		ebitenutil.DebugPrintAt(screen, fmt.Sprintf("healthGain: %0.2f", food.healthGain), int(food.x), int(food.y))
	}
}

func (f *Fish) OutOfBoundsDetection() {
	if f.x <= 0 || f.x >= float64(WINDOW_WIDTH) {
		f.vx = -f.vx
	}

	if f.y <= 0 || f.y >= float64(WINDOW_HEIGHT) {
		f.vy = -f.vy
	}
}

func (f *Fish) LifeTick(g *Game) {
	if ebiten.ActualTPS() < 0.5 {
		return
	}
	vsecond := (1 / ebiten.ActualTPS()) * TIME_MULTIPLIER
	f.health -= vsecond + 0.005 // make them loose life faster, to make sure it's generating new fishes
	f.age += vsecond
	f.lastReproduction += vsecond
	if f.health <= 0 {
		// Remove it from g.fishes
		for i, fish := range g.fishes.fishes {
			if fish == f {
				g.fishes.fishes = append(g.fishes.fishes[:i], g.fishes.fishes[i+1:]...)
				break
			}
		}
	}
	if f.age > 10 && f.health > 50 && f.lastReproduction > 10 {
		f.canReproduce = true
	} else {
		f.canReproduce = false
	}

	if f.canReproduce {
		for _, fish := range f.NearbyFishes(g) {
			fish.lastReproduction = 0
			f.lastReproduction = 0

			// Generate the new fish based on the attributes of their parents
			newspeed := (f.speed + fish.speed) / 2
			newvision := (f.vision + fish.vision) / 2
			// Genetic variation 1/1000 chance for each attribute
			if rand.Intn(1000) == 0 {
				newspeed += rand.Float64()*2 - 1
			}
			if rand.Intn(1000) == 0 {
				newvision += rand.Float64()*2 - 1
			}
			g.fishes.fishes = append(g.fishes.fishes, &Fish{imageWidth: FISH_SIZE, imageHeight: FISH_SIZE, x: (f.x + fish.x) / 2, y: (f.y + fish.y) / 2, vx: 0, vy: 0, speed: newspeed, vision: newvision, lastReproduction: 0, health: 90 + math.Floor(rand.Float64()*10), age: 0})
			if g.fishes.fishes[len(g.fishes.fishes)-1].speed <= 0.05 {
				g.fishes.fishes[len(g.fishes.fishes)-1].speed = 0.05
			}
			g.fishes.fishes[len(g.fishes.fishes)-1].RandDirectionAndSpeed()
		}
	}
	for _, food := range f.NearbyFood(g) {
		// Make the fish go towards the food
		f.vx = (food.x - f.x) / (20 - f.speed)
		f.vy = (food.y - f.y) / (20 - f.speed)
		// remove food as it got eaten
		distance := math.Sqrt(math.Pow(f.x-food.x, 2) + math.Pow(f.y-food.y, 2))
		if distance < 1.5 {
			for i, cfood := range g.foods {
				if cfood == food {
					g.foods = append(g.foods[:i], g.foods[i+1:]...)
					break
				}
			}
			f.health += food.healthGain
			f.RandDirectionAndSpeed()
		}
	}
}
func (f *Fish) NearbyFishes(g *Game) []*Fish {
	var result []*Fish
	for _, fish := range g.fishes.fishes {
		if fish == f {
			continue
		}
		distance := math.Sqrt(math.Pow(f.x-fish.x, 2) + math.Pow(f.y-fish.y, 2))
		if distance <= f.vision {
			result = append(result, fish)
		}
	}
	return result
}

func (f *Fish) NearbyFood(g *Game) []*Food {
	var result []*Food
	for _, food := range g.foods {
		distance := math.Sqrt(math.Pow(f.x-food.x, 2) + math.Pow(f.y-food.y, 2))
		if distance <= f.vision {
			result = append(result, food)
		}
	}
	return result
}

func (f *Fish) RandDirectionAndSpeed() {
	directionX, directionY := rand.Intn(2)-1, rand.Intn(2)-1
	if directionX == 0 {
		directionX = 1
	}
	if directionY == 0 {
		directionY = 1
	}

	f.vx = float64(directionX) * f.speed
	f.vy = float64(directionY) * f.speed
}

func (g *Game) Layout(outsideWidth, outsideHeight int) (screenWidth, screenHeight int) {

	return WINDOW_WIDTH, WINDOW_HEIGHT
}

func main() {
	args := os.Args
	ebiten.SetTPS(165)
	for i, arg := range args {
		switch arg {
		case "--fullscreen":
			ebiten.SetFullscreen(true)
		case "--screen":
			w, h := ebiten.ScreenSizeInFullscreen()
			WINDOW_WIDTH = w
			WINDOW_HEIGHT = h
		case "--tps":
			if len(args) == i+1 {
				fmt.Println("Usage: --tps <limit>")
				os.Exit(1)
			}
			parsed, err := strconv.Atoi(args[i+1])
			if err != nil {
				fmt.Println("Invalid TPS")
				os.Exit(1)
			}
			ebiten.SetTPS(parsed)
		case "--vsync-off":
			ebiten.SetVsyncEnabled(false)
		case "--time-multiplier":
			if len(args) == i+1 {
				fmt.Println("Usage: --time-multiplier <limit>")
				os.Exit(1)
			}
			parsed, err := strconv.ParseFloat(args[i+1], 64)
			if err != nil {
				fmt.Println("Invalid time multiplier")
				os.Exit(1)
			}
			TIME_MULTIPLIER = parsed
		}
	}
	ebiten.SetWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
	ebiten.SetWindowTitle("Fishsim")

	if err := ebiten.RunGame(&Game{}); err != nil {
		log.Fatal(err)
	}
	select {}
}
