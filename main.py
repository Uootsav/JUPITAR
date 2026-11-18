import os,sys
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
if __name__=='__main__':
    if '--self-test' in sys.argv:
        from jupitar.selftest import run
        i=sys.argv.index('--self-test')
        raise SystemExit(run(sys.argv[i+1]))
    from jupitar.desktop import main
    main()
