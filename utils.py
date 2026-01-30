from time import perf_counter

def get_trss(proc):
    return perf_counter(), proc.memory_info().rss

def rigid_evaluation_on_provided_examples(cap, sample_output, proc, t0, r0, tmax, rmax):
    try:
        assert len(cap.stdout.strip()) > 0, "❌  no output found! Did you forget '%%capture cap'?"
        assert cap.stdout.strip() == sample_output.strip(), "❌  output differs!"
        print("✅  matches expected output")
    except AssertionError as e:
        print(e)

    t1, r1 = get_trss(proc)

    print(f"Time (sec): {t1-t0:>10.3e}")
    print(f"RSS (B): {r1-r0:>13.3e}")
    assert (t1-t0 <= tmax and r1-r0 <= rmax), "❌  your code isn't efficient enough! Check time/space limits."
    print("✅  efficient enough")