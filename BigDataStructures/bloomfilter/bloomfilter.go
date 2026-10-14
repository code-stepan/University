package bloomfilter

import (
	"fmt"
	"hash"
	"math"
	"sync"
)

type BloomFilter struct {
	bitSet []bool
	m      uint64 // количество битов в наборе типов
	hashes []hash.Hash64
	k      uint64 // количество исспользуемых хэш функций
	mutex  sync.Mutex
}

func NewBloomFilter(n uint64, p float64, h Hasher) (*BloomFilter, error) {
	if n == 0 {
		return nil, fmt.Errorf("количество элементов не может быть 0")
	}
	if p <= 0 || p >= 1 {
		return nil, fmt.Errorf("ложно позитивная вероятность должнать быть в пределах от 0 до 1")
	}
	if h == nil {
		return nil, fmt.Errorf("hasher не может быть равен nil")
	}
	m, k := optimalParams(n, p)
	return &BloomFilter{
		m:      m,
		k:      k,
		bitSet: make([]bool, m),
		hashes: h.GetHashes(k),
	}, nil
}

func optimalParams(n uint64, p float64) (uint64, uint64) {
	m := uint64(math.Ceil(-1 * float64(n) * math.Log(p) / math.Pow(math.Log(2), 2)))
	if m == 0 {
		m = 1
	}
	k := uint64(math.Ceil((float64(m) / float64(n)) * math.Log(2)))
	if k == 0 {
		k = 1
	}
	return m, k
}

func (bf *BloomFilter) Add(data []byte) {
	bf.mutex.Lock()
	defer bf.mutex.Unlock()
	for _, hash := range bf.hashes {
		hash.Reset()
		hash.Write(data)
		hashValue := hash.Sum64() % bf.m
		bf.bitSet[hashValue] = true
	}
}

func (bf *BloomFilter) Test(data []byte) bool {
	bf.mutex.Lock()
	defer bf.mutex.Unlock()
	for _, hash := range bf.hashes {
		hash.Reset()
		hash.Write(data)
		hashValue := hash.Sum64() % bf.m
		if !bf.bitSet[hashValue] {
			return false
		}
	}
	return true
}
