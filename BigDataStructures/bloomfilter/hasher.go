package bloomfilter

import (
	"hash"

	"github.com/spaolacci/murmur3"
)

type MurMur3hasher struct{}

func NewMurMur3Hasher() *MurMur3hasher {
	return &MurMur3hasher{}
}

func (h MurMur3hasher) GetHashes(n uint64) []hash.Hash64 {
	hashers := make([]hash.Hash64, n)
	for i := 0; uint64(i) < n; i++ {
		hashers[i] = murmur3.New64WithSeed(uint32(i))
	}
	return hashers
}
