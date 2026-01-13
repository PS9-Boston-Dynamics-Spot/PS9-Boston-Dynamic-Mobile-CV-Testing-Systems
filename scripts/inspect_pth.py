import sys, torch, json

p = (
    sys.argv[1]
    if len(sys.argv) > 1
    else "src/common/cvision/notebooks/models/resnet34-stage-final.pth"
)
print("Path:", p)
try:
    obj = torch.load(p, map_location="cpu", weights_only=True)
    print("Loaded with weights_only=True, type:", type(obj))
except Exception as e:
    print("weights_only load failed:", e)
    try:
        # controlled unpickle only for inspection (requires fastcore installed)
        import fastcore.foundation as _ff

        try:
            with torch.serialization.safe_globals([_ff.L]):
                obj = torch.load(p, map_location="cpu", weights_only=False)
        except AttributeError:
            torch.serialization.add_safe_globals([_ff.L])  # type: ignore
            obj = torch.load(p, map_location="cpu", weights_only=False)
        print("Loaded with full unpickle, type:", type(obj))
    except Exception as e2:
        print("full unpickle failed:", e2)
        raise SystemExit(1)
# summary
if isinstance(obj, dict):
    print("dict keys count:", len(obj.keys()))
    sample = list(obj.keys())[:50]
    print("sample keys:", json.dumps(sample))
else:
    print("object repr:", repr(obj)[:1000])
    # try to detect model/state_dict attributes
    if hasattr(obj, "state_dict"):
        sd = obj.state_dict()
        print("object has state_dict with keys:", list(sd.keys())[:20])
    elif hasattr(obj, "model"):
        print("object has attribute 'model' of type", type(obj.model))
        try:
            sd = getattr(obj, "model")
            if hasattr(sd, "state_dict"):
                print(
                    "model.state_dict keys sample:", list(sd.state_dict().keys())[:20]
                )
        except Exception:
            pass
