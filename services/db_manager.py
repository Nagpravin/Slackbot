from supabase import create_client
import config

supabase=create_client(config.SUPABASE_URL,config.SUPABASE_KEY)

def save_keywords(user_id,raw,cleaned):
    data={"user_id":user_id,"raw_keywords":raw,"cleaned_keywords":cleaned}
    res=supabase.table("keywords").insert(data).execute()
    return res

def save_clusters(user_id,clusters):
    try:
        # get latest id for user
        res=supabase.table("keywords").select("id").eq("user_id",user_id).order("id",desc=True).limit(1).execute()
        if len(res.data)==0:
            print("no record for user")
            return None
        last_id=res.data[0]["id"]
        up=supabase.table("keywords").update({"clusters":clusters}).eq("id",last_id).execute()
        return up
    except Exception as e:
        print("db err:",e)
        return None
