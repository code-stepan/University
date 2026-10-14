package countminsketch

import (
	"hash"
	"hash/fnv"
	"math"
)

type CountMinSketch struct {
	d     uint
	w     uint
	table [][]uint
	hash  hash.Hash64
}

func New(epsilon, delta float64) *CountMinSketch {
	if epsilon <= 0 || epsilon >= 1 {
		panic("epsilon must be in (0, 1)")
	}
	if delta <= 0 || delta >= 1 {
		panic("delta must be in (0, 1)")
	}
	w := uint(math.Ceil(math.E / epsilon))
	d := uint(math.Ceil(math.Log(1 / delta)))
	table := make([][]uint, d)
	for i := range table {
		table[i] = make([]uint, w)
	}
	return &CountMinSketch{d: d, w: w, table: table, hash: fnv.New64a()}
}

func (cms *CountMinSketch) hashFn(i uint, data []byte) uint {
	cms.hash.Reset()
	cms.hash.Write([]byte{byte(i), byte(i >> 8), byte(i >> 16), byte(i >> 24)})
	cms.hash.Write(data)
	return uint(cms.hash.Sum64()) % cms.w
}

func (cms *CountMinSketch) Add(data []byte) {
	for i := uint(0); i < cms.d; i++ {
		j := cms.hashFn(i, data)
		cms.table[i][j]++
	}
}

func (cms *CountMinSketch) Count(data []byte) uint {
	var min uint = ^uint(0)
	for i := uint(0); i < cms.d; i++ {
		j := cms.hashFn(i, data)
		if cms.table[i][j] < min {
			min = cms.table[i][j]
		}
	}
	return min
}
