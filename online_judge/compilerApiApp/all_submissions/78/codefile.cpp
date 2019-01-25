                        #include<bits/stdc++.h>
using namespace std;
#define PB(x) push_back(x)
#define MP(x,y) make_pair(x,y)
#define ll  long long int 
#define F first
#define S second
#define boost ios_base::sync_with_stdio(false),cin.tie(NULL);
const ll MOD = 1000000007;

long long int getmid(long long int n)
{
    long long int count1 = 0;
    for(long long int i=2;i<=1000000000000000000;i*=2)
    {
        long long int a = n/i,fg=i/2;
        long long int rem = n%i;
        
        count1 += (a*(i/2));
        if((rem-(i/2-1))>=0)
        {
            count1+=(rem-(i/2-1));
        }
    }
    
    return count1;
}
int main()
{
  //  boost
    //#ifndef ONLINE_JUDGE
      //  freopen("input.txt", "r", stdin);
        //freopen("output.txt", "w", stdout);
    //#endif
    long long int t,x,sum,ans,i; 
    cin>>t;
    while(t--)
    {
        cin>>x;
        long long int l=1,r=100000000000000000;
        
        while((r-l)>2)
        {
            long long int mid = (l+r)/2;
            long long int y = getmid(mid);
            if(y == x)
            {
                ans = mid;
                break;
            }
            else if(y>x)
            {
                r = mid;
                ans = mid;
            }
            else if(y<x)
            {
                l = mid;
            }
        }
        while(l<=r)
        {
            long long int y = getmid(l);
            if(y>=x)
            {
                ans = l;
                break;
            }
            l++;
        }
        cout<<ans<<endl;
	//cout<<getmid(ans)<<endl;
    }
    return 0;
}
