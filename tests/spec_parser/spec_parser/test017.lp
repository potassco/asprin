% asprin test17.lp
% ERROR

1 { a(X) : dom(X) }.
dom(1..3).
#show a/1.

#preference(p, subset){ 
  a(1;2)
} : v.
#optimize(p).

%asprin version 3.0.0
%Reading from tests/spec_parser/spec_parser/test017.lp
%<block>:1:26-27: info: atom does not occur in any rule head:
%  v
%
%  <block>:2:53-54: info: atom does not occur in any rule head:
%    v
%
%    <block>:3:31-32: info: atom does not occur in any rule head:
%      v
%
%      <block>:4:53-54: info: atom does not occur in any rule head:
%        v
%
%        <block>:5:31-32: info: atom does not occur in any rule head:
%          v
%
%          optimize:p: error: preference specification error, optimizing non existent preference statement
%
%          *** ERROR: (asprin): parsing failed
%          UNKNOWN
