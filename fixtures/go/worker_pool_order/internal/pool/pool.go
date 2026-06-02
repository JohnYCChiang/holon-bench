package pool

type Job struct {
	ID    int
	Value int
}

type Result struct {
	ID    int
	Value int
}

func Process(jobs []Job, workers int) []Result {
	results := make([]Result, len(jobs))
	for i, job := range jobs {
		results[len(jobs)-1-i] = Result{ID: job.ID, Value: job.Value * 2}
	}
	return results
}
