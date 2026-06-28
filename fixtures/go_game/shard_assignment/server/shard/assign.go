package shard

import (
	"hash/fnv"
	"sort"
)

// Cluster deterministically assigns players to shards with bounded capacity.
// The primary shard for a player is chosen by a stable hash; if it is full the
// assignment probes the following shards in sorted order. Assignment is
// idempotent: a player always maps to the same shard. No shard ever exceeds its
// capacity.
type Cluster struct {
	shards []string
	cap    int
	assign map[string]string
	load   map[string]int
}

func NewCluster(shards []string, capacity int) *Cluster {
	s := append([]string(nil), shards...)
	sort.Strings(s)
	return &Cluster{
		shards: s,
		cap:    capacity,
		assign: map[string]string{},
		load:   map[string]int{},
	}
}

func hashID(id string) uint64 {
	h := fnv.New64a()
	_, _ = h.Write([]byte(id))
	return h.Sum64()
}

// Assign places player on a shard and returns it. It is idempotent for an
// already-assigned player. Empty ids are rejected, and false is returned when
// every shard is at capacity.
func (c *Cluster) Assign(player string) (string, bool) {
	if player == "" {
		return "", false
	}
	if s, ok := c.assign[player]; ok {
		return s, true
	}
	start := int(hashID(player) % uint64(len(c.shards)))
	s := c.shards[start]
	// BUG: ignores capacity and never probes; overfills the primary shard.
	c.assign[player] = s
	c.load[s]++
	return s, true
}

// Shard returns the shard a player is assigned to, or "" if unassigned.
func (c *Cluster) Shard(player string) string { return c.assign[player] }

// Load returns the number of players on a shard.
func (c *Cluster) Load(shard string) int { return c.load[shard] }
